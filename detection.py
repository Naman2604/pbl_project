import cv2
import numpy as np
from ultralytics import YOLO

# Load YOLOv8 nano model (fast, good accuracy; swap for yolov8s.pt or yolov8m.pt for better accuracy at cost of speed)
model = YOLO("yolov8n.pt")  # Downloads automatically on first run (~6MB)

# COCO class IDs for vehicles
VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

# Confidence threshold — lower this if you're missing detections, raise to reduce false positives
CONFIDENCE_THRESHOLD = 0.35

def process_frame(frame):
    """
    Detect vehicles in a frame using YOLOv8.
    Returns the annotated frame and a slot_data list (1=occupied, 0=free).
    """
    results = model(frame, verbose=False)[0]

    slot_data = []
    detected_boxes = []

    for box in results.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])

        if cls_id in VEHICLE_CLASSES and conf >= CONFIDENCE_THRESHOLD:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label = f"{VEHICLE_CLASSES[cls_id]} {conf:.2f}"

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

            slot_data.append(1)
            detected_boxes.append((x1, y1, x2, y2))

    # Pad to total_slots
    total_slots = max(10, len(slot_data))
    while len(slot_data) < 10:
        slot_data.append(0)

    return frame, slot_data