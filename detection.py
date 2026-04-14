import cv2
import numpy as np

# ──────────────────────────────────────────────────────────────
# PARKING SLOT ROIs  →  (x, y, width, height)
#
# These are mapped to your parking.mp4 frame (assumed ~640×480).
# Run the calibration helper to get exact values for YOUR video:
#
#   python detection.py calibrate
#
# Then paste the printed coordinates below.
# ──────────────────────────────────────────────────────────────
PARKING_SLOTS = [
    (30,  200, 100, 70),   # Slot 1
    (140, 200, 100, 70),   # Slot 2
    (250, 200, 100, 70),   # Slot 3
    (360, 200, 100, 70),   # Slot 4
    (470, 200, 100, 70),   # Slot 5
    (30,  310, 100, 70),   # Slot 6
    (140, 310, 100, 70),   # Slot 7
    (250, 310, 100, 70),   # Slot 8
    (360, 310, 100, 70),   # Slot 9
    (470, 310, 100, 70),   # Slot 10
]

TOTAL_SLOTS     = len(PARKING_SLOTS)
OCCUPIED_RATIO  = 0.35    # >35% changed pixels in ROI = occupied
BG_HISTORY      = 500
BG_THRESHOLD    = 50

_bg_sub = cv2.createBackgroundSubtractorMOG2(
    history=BG_HISTORY,
    varThreshold=BG_THRESHOLD,
    detectShadows=True
)
_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))


def process_frame(frame):
    """
    Returns
    -------
    annotated_frame : np.ndarray
    slot_data       : list[int]  — 1=occupied, 0=free, len == TOTAL_SLOTS
    """
    fh, fw = frame.shape[:2]

    # 1. Build foreground mask, remove shadows and noise
    fg = _bg_sub.apply(frame)
    _, fg = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, _kernel, iterations=2)
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN,  _kernel, iterations=1)

    # 2. Evaluate each slot
    slot_data = []
    annotated = frame.copy()

    for idx, (x, y, w, h) in enumerate(PARKING_SLOTS):
        x1, y1 = max(0, x),       max(0, y)
        x2, y2 = min(fw, x + w),  min(fh, y + h)

        roi        = fg[y1:y2, x1:x2]
        fill_ratio = np.count_nonzero(roi) / roi.size if roi.size > 0 else 0
        occupied   = fill_ratio > OCCUPIED_RATIO
        slot_data.append(1 if occupied else 0)

        color = (0, 0, 220) if occupied else (0, 210, 0)

        overlay = annotated.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
        cv2.addWeighted(overlay, 0.20, annotated, 0.80, 0, annotated)
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        cv2.putText(annotated, f"P{idx+1}", (x1 + 4, y1 + 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)

    # 3. HUD summary bar
    occ  = sum(slot_data)
    free = TOTAL_SLOTS - occ
    rate = (occ / TOTAL_SLOTS * 100) if TOTAL_SLOTS else 0
    hud  = f"  Total: {TOTAL_SLOTS}   Occupied: {occ}   Free: {free}   Rate: {rate:.0f}%"
    cv2.rectangle(annotated, (0, 0), (fw, 26), (15, 15, 15), -1)
    cv2.putText(annotated, hud, (6, 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.52, (210, 210, 210), 1, cv2.LINE_AA)

    return annotated, slot_data


# ── Standalone test / calibration ────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        video = sys.argv[2] if len(sys.argv) > 2 else "parking.mp4"
        cap   = cv2.VideoCapture(video)
        ret, frame = cap.read(); cap.release()
        if not ret: print("[ERROR] Cannot read frame."); sys.exit(1)

        slots, pts, clone = [], [], frame.copy()

        def _click(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                pts.append((x, y))
                cv2.circle(clone, (x, y), 4, (0, 255, 255), -1)
                cv2.imshow("Calibrate", clone)
                if len(pts) == 2:
                    x1, y1 = pts[0]; x2, y2 = pts[1]
                    sw, sh = abs(x2-x1), abs(y2-y1)
                    slots.append((min(x1,x2), min(y1,y2), sw, sh))
                    cv2.rectangle(clone, pts[0], pts[1], (0,255,0), 2)
                    cv2.imshow("Calibrate", clone)
                    pts.clear()
                    print(f"  Slot {len(slots)}: ({min(x1,x2)}, {min(y1,y2)}, {sw}, {sh})")

        cv2.imshow("Calibrate", clone); cv2.setMouseCallback("Calibrate", _click)
        print("Click TOP-LEFT then BOTTOM-RIGHT of each slot. Press 'n' when done.")
        while cv2.waitKey(1) & 0xFF != ord('n'): pass
        cv2.destroyAllWindows()
        print("\nPaste into PARKING_SLOTS:\n\nPARKING_SLOTS = [")
        for s in slots: print(f"    {s},")
        print("]")

    else:
        video = sys.argv[1] if len(sys.argv) > 1 else "parking.mp4"
        cap   = cv2.VideoCapture(video)
        if not cap.isOpened(): print(f"[ERROR] Cannot open: {video}"); sys.exit(1)
        print("Press 'q' to quit.")
        while True:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0); continue
            result, _ = process_frame(frame)
            cv2.imshow("Detection", result)
            if cv2.waitKey(30) & 0xFF == ord('q'): break
        cap.release(); cv2.destroyAllWindows()
