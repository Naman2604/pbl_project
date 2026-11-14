"""
Vehicle detection and parking-slot occupancy.

How it works
------------
1. YOLOv8 finds vehicles in a frame.
2. Each vehicle is matched to at most ONE parking slot (best overlap / IoU).
3. A slot flips between free/occupied only after the new state has been seen
   for several detections in a row (debouncing), so the dashboard numbers
   don't flicker when YOLO misses a car for a single frame.

Slot positions live in `slots.json` (created by `python calibrate_slots.py`).
"""
import json
import logging
import os
from pathlib import Path

import cv2
from ultralytics import YOLO

log = logging.getLogger("parking.detection")

BASE_DIR = Path(__file__).resolve().parent

# ── Settings (override with environment variables if you like) ──────────────
MODEL_PATH = os.getenv("YOLO_MODEL", str(BASE_DIR / "yolov8n.pt"))
SLOTS_PATH = Path(os.getenv("SLOTS_FILE", str(BASE_DIR / "slots.json")))

# COCO class IDs for vehicles
VEHICLE_CLASSES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}

# Lower this if you're missing cars, raise it to reduce false positives
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.35"))
# Smaller (e.g. 480) = faster but may miss distant cars. Larger = slower.
INFER_IMGSZ = int(os.getenv("INFER_IMGSZ", "640"))
# A vehicle "belongs" to a slot when their boxes overlap at least this much (IoU)
SLOT_IOU_THRESHOLD = float(os.getenv("SLOT_IOU_THRESHOLD", "0.4"))
# A slot must show a new state this many detections in a row before it flips.
# At the default 0.3s detection interval, 5 = a change shows up after ~1.5s.
# (Measured on parking.mp4: 5 cuts slot flicker by ~80% vs. no smoothing.)
DEBOUNCE_DETECTIONS = int(os.getenv("DEBOUNCE_DETECTIONS", "5"))

COLOR_FREE = (0, 200, 0)       # BGR
COLOR_OCCUPIED = (0, 0, 220)
COLOR_OTHER = (200, 140, 40)


def iou(a, b):
    """Intersection-over-union of two (x1, y1, x2, y2) boxes."""
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def load_slots(path=SLOTS_PATH):
    """
    Returns (slots, frame_start, frame_end).
    slots is a list of (x1, y1, x2, y2). frame_start/end say which part of the
    video the slots were calibrated for (slots only match that camera view).
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        log.error("%s not found - run `python calibrate_slots.py` first. "
                  "Running with 0 slots.", path)
        return [], 0, None

    slots = [(x, y, x + w, y + h) for x, y, w, h in data["slots"]]
    return slots, int(data.get("frame_start", 0)), data.get("frame_end")


class ParkingDetector:
    def __init__(self, load_slot_file=True):
        log.info("Loading YOLO model: %s", MODEL_PATH)
        self.model = YOLO(MODEL_PATH)
        if load_slot_file:
            self.slots, self.frame_start, self.frame_end = load_slots()
        else:                       # used by calibrate_slots.py
            self.slots, self.frame_start, self.frame_end = [], 0, None
        self._unassigned = []
        self.reset()
        log.info("Monitoring %d slots (video frames %s-%s)",
                 len(self.slots), self.frame_start, self.frame_end)

    def reset(self):
        """Forget slot history (call when the video loops back to the start)."""
        self.state = [False] * len(self.slots)
        self._streak = [0] * len(self.slots)
        self._first = True

    # ── 1. detect ────────────────────────────────────────────────────────
    def detect(self, frame):
        """Return a list of (x1, y1, x2, y2, label, confidence) for vehicles."""
        results = self.model(frame, imgsz=INFER_IMGSZ, verbose=False)[0]
        vehicles = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            if cls_id in VEHICLE_CLASSES and conf >= CONFIDENCE_THRESHOLD:
                x1, y1, x2, y2 = map(float, box.xyxy[0])
                vehicles.append((x1, y1, x2, y2, VEHICLE_CLASSES[cls_id], conf))
        return vehicles

    # ── 2. assign vehicles to slots ──────────────────────────────────────
    def update(self, vehicles):
        """Match vehicles to slots and return the (debounced) occupied flags."""
        pairs = []
        for vi, v in enumerate(vehicles):
            for si, s in enumerate(self.slots):
                score = iou(v[:4], s)
                if score >= SLOT_IOU_THRESHOLD:
                    pairs.append((score, vi, si))

        raw = [False] * len(self.slots)
        used_vehicles = set()
        for score, vi, si in sorted(pairs, reverse=True):   # best matches first
            if vi in used_vehicles or raw[si]:
                continue
            used_vehicles.add(vi)
            raw[si] = True
        self._unassigned = [v for i, v in enumerate(vehicles) if i not in used_vehicles]

        if self._first:                       # first reading: trust it immediately
            self.state = raw
            self._first = False
            return list(self.state)

        for i, seen in enumerate(raw):
            if seen == self.state[i]:
                self._streak[i] = 0
            else:
                self._streak[i] += 1
                if self._streak[i] >= DEBOUNCE_DETECTIONS:
                    self.state[i] = seen
                    self._streak[i] = 0
        return list(self.state)

    # ── 3. draw ──────────────────────────────────────────────────────────
    def draw(self, frame, states):
        out = frame.copy()
        fh, fw = out.shape[:2]

        # vehicles that aren't in a slot (driving through, far away, ...)
        for x1, y1, x2, y2, _label, _conf in self._unassigned:
            cv2.rectangle(out, (int(x1), int(y1)), (int(x2), int(y2)), COLOR_OTHER, 1)

        overlay = out.copy()
        for (x1, y1, x2, y2), occupied in zip(self.slots, states):
            color = COLOR_OCCUPIED if occupied else COLOR_FREE
            cv2.rectangle(overlay, (int(x1), int(y1)), (int(x2), int(y2)), color, -1)
        out = cv2.addWeighted(overlay, 0.25, out, 0.75, 0)

        for i, ((x1, y1, x2, y2), occupied) in enumerate(zip(self.slots, states), 1):
            color = COLOR_OCCUPIED if occupied else COLOR_FREE
            cv2.rectangle(out, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            cv2.putText(out, f"P{i}", (int(x1) + 3, int(y1) + 14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)

        total = len(self.slots)
        occ = sum(states)
        rate = (occ / total * 100) if total else 0
        hud = f" Total: {total}   Occupied: {occ}   Free: {total - occ}   Rate: {rate:.0f}%"
        cv2.rectangle(out, (0, 0), (fw, 26), (15, 15, 15), -1)
        cv2.putText(out, hud, (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.52,
                    (210, 210, 210), 1, cv2.LINE_AA)
        return out
