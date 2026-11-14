"""
Automatically find parking slots in a fixed-camera video.

Idea: a spot where a vehicle stays parked for a good part of the video is a
parking slot. We sample frames, run YOLO, group detections that keep showing
up in the same place, and save those places to `slots.json`.

Usage
-----
    python calibrate_slots.py                      # whole video
    python calibrate_slots.py --end 4650           # only frames 0-4650

IMPORTANT: slots only make sense for ONE camera view. If your video contains
a camera cut or pan (the bundled parking.mp4 changes view after ~frame 4650),
pass --end so only the first view is used. The app loops just that range.
It prints a warning when it spots a possible camera change.
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np

from detection import ParkingDetector, iou

BASE_DIR = Path(__file__).resolve().parent


def thumb(frame):
    return cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (64, 36)).astype(float)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--video", default=str(BASE_DIR / "parking.mp4"))
    p.add_argument("--start", type=int, default=0, help="first frame to use")
    p.add_argument("--end", type=int, default=None, help="last frame to use (default: end of video)")
    p.add_argument("--step", type=int, default=30, help="sample every N frames")
    p.add_argument("--min-support", type=float, default=0.15,
                   help="a slot must be occupied in at least this fraction of samples (default 0.15)")
    p.add_argument("--out", default=str(BASE_DIR / "slots.json"))
    p.add_argument("--preview", default=str(BASE_DIR / "slots_preview.jpg"))
    args = p.parse_args()

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        raise SystemExit(f"Cannot open video: {args.video}")
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    end = min(args.end, total) if args.end else total

    detector = ParkingDetector(load_slot_file=False)
    samples, prev_thumb, first_frame = [], None, None

    print(f"Sampling frames {args.start}-{end} every {args.step} ...")
    for idx in range(args.start, end, args.step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        if not ok:
            break
        if first_frame is None:
            first_frame = frame
        t = thumb(frame)
        if prev_thumb is not None and np.abs(t - prev_thumb).mean() > 30:
            print(f"  ! big visual change near frame {idx} - possible camera cut/pan. "
                  f"If slots look wrong, re-run with --end {idx - args.step}.")
        prev_thumb = t
        samples.append([v[:4] for v in detector.detect(frame)])
    cap.release()
    if not samples:
        raise SystemExit("No frames could be read.")

    # Group detections that overlap strongly across samples
    clusters = []   # each: {"box": mean box, "n": count, "sum": running sum}
    for boxes in samples:
        for b in boxes:
            best, best_iou = None, 0.5
            for c in clusters:
                v = iou(c["box"], b)
                if v > best_iou:
                    best, best_iou = c, v
            if best is None:
                clusters.append({"box": list(b), "n": 1, "sum": list(b)})
            else:
                best["n"] += 1
                best["sum"] = [s + x for s, x in zip(best["sum"], b)]
                best["box"] = [s / best["n"] for s in best["sum"]]

    # Keep spots that are occupied often enough, drop near-duplicates
    min_n = args.min_support * len(samples)
    kept = sorted((c for c in clusters if c["n"] >= min_n), key=lambda c: -c["n"])
    slots = []
    for c in kept:
        if all(iou(c["box"], s["box"]) < 0.3 for s in slots):
            slots.append(c)
    # number slots top-to-bottom, left-to-right so P1, P2... are predictable
    slots.sort(key=lambda c: (round(c["box"][1] / 40), c["box"][0]))

    out = {
        "video": Path(args.video).name,
        "frame_start": args.start,
        "frame_end": end,
        "slots": [[round(b[0]), round(b[1]), round(b[2] - b[0]), round(b[3] - b[1])]
                  for b in (c["box"] for c in slots)],
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)

    preview = first_frame.copy()
    for i, (x, y, w, h) in enumerate(out["slots"], 1):
        cv2.rectangle(preview, (x, y), (x + w, y + h), (0, 255, 255), 1)
        cv2.putText(preview, f"P{i}", (x + 2, y + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
    cv2.imwrite(args.preview, preview)

    print(f"\nFound {len(out['slots'])} slots from {len(samples)} sampled frames.")
    print(f"Saved {args.out}\nPreview image: {args.preview}  (open it and check the boxes look right)")


if __name__ == "__main__":
    main()
