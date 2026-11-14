"""
Flask backend for the Smart Parking system.

A single background thread reads the video, runs detection a few times per
second, updates the stats, and keeps the latest annotated JPEG in memory.
Every browser that opens /video_feed just receives that latest frame, so:
  * stats stay live even when nobody is watching the video,
  * many viewers don't slow each other down or fight over the video file.

Run locally:      python app.py
Run in production: gunicorn app:app --workers 1 --threads 16 --timeout 120
(keep --workers at 1: the detector and its stats live inside one process)
"""
import logging
import os
import threading
import time

import cv2
from flask import Flask, Response, jsonify
from flask_cors import CORS

from analytics import get_slots, get_stats, update_stats
from detection import BASE_DIR, ParkingDetector

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("parking.app")

VIDEO_PATH = os.getenv("VIDEO_PATH", str(BASE_DIR / "parking.mp4"))
STREAM_FPS = float(os.getenv("STREAM_FPS", "15"))            # frames sent to browsers per second
DETECT_INTERVAL = float(os.getenv("DETECT_INTERVAL", "0.3"))  # seconds between YOLO runs
JPEG_QUALITY = int(os.getenv("JPEG_QUALITY", "70"))


class FrameProducer(threading.Thread):
    """Reads the video, runs detection, and publishes the newest JPEG frame."""

    def __init__(self):
        super().__init__(daemon=True, name="frame-producer")
        self._cond = threading.Condition()
        self._jpeg = None
        self._frame_id = 0
        self.last_frame_time = None
        self.video_open = False
        self.last_error = None
        self.detections_run = 0
        self.slot_count = 0
        self._detector = None

    # ── used by the Flask routes ─────────────────────────────────────────
    def wait_for_frame(self, last_id, timeout=10):
        with self._cond:
            self._cond.wait_for(lambda: self._frame_id != last_id, timeout)
            return self._frame_id, self._jpeg

    def _publish(self, jpeg):
        with self._cond:
            self._jpeg = jpeg
            self._frame_id += 1
            self.last_frame_time = time.time()
            self._cond.notify_all()

    # ── background loop ──────────────────────────────────────────────────
    def run(self):
        while True:       # never let an error silently kill the stats
            try:
                self._run_once()
            except Exception as exc:            # noqa: BLE001
                self.last_error = repr(exc)
                self.video_open = False
                log.exception("Frame producer stopped; restarting in 3s")
                time.sleep(3)

    def _run_once(self):
        if self._detector is None:          # load the model once, not on every retry
            self._detector = ParkingDetector()
        detector = self._detector
        self.slot_count = len(detector.slots)
        cap = cv2.VideoCapture(VIDEO_PATH)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video: {VIDEO_PATH}")
        self.video_open = True
        self.last_error = None

        src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        step = max(1, round(src_fps / STREAM_FPS))   # source frames per streamed frame
        period = 1.0 / STREAM_FPS
        start = detector.frame_start
        end = detector.frame_end or int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        cap.set(cv2.CAP_PROP_POS_FRAMES, start)
        pos, just_wrapped = start, True
        states = [False] * len(detector.slots)
        last_detect = 0.0
        next_tick = time.monotonic()

        while True:
            ok, frame = cap.read() if pos < end else (False, None)
            if not ok:
                if just_wrapped:
                    raise RuntimeError("Could not read any frames from the video")
                # Reached the end of the calibrated range: loop back to the start
                pos, just_wrapped, last_detect = start, True, 0.0
                cap.set(cv2.CAP_PROP_POS_FRAMES, start)
                detector.reset()
                continue
            just_wrapped = False
            pos += 1

            if time.monotonic() - last_detect >= DETECT_INTERVAL:
                vehicles = detector.detect(frame)
                states = detector.update(vehicles)
                update_stats(states)
                self.detections_run += 1
                last_detect = time.monotonic()

            annotated = detector.draw(frame, states)
            ok, buf = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
            if ok:
                self._publish(buf.tobytes())

            # Skip source frames so the video plays at normal speed
            for _ in range(step - 1):
                cap.grab()
                pos += 1

            # Pace the loop; if we're running behind, drop frames instead of slowing down
            next_tick += period
            delay = next_tick - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            elif -delay > period:
                for _ in range(int(-delay / period) * step):
                    cap.grab()
                    pos += 1
                next_tick = time.monotonic()


app = Flask(__name__)
CORS(app)

producer = FrameProducer()
producer.start()


@app.after_request
def no_cache(resp):
    resp.headers["Cache-Control"] = "no-store"
    return resp


def mjpeg_stream():
    last_id = -1
    while True:
        frame_id, jpeg = producer.wait_for_frame(last_id)
        if jpeg is None or frame_id == last_id:     # still starting up / timed out
            continue
        last_id = frame_id
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n")


@app.route("/")
def index():
    return jsonify(name="Smart Parking API",
                   endpoints=["/video_feed", "/api/stats", "/api/slots", "/health"])


@app.route("/video_feed")
def video_feed():
    return Response(mjpeg_stream(),
                    mimetype="multipart/x-mixed-replace; boundary=frame",
                    headers={"X-Accel-Buffering": "no"})


@app.route("/api/stats")
def api_stats():
    return jsonify(get_stats())


@app.route("/api/slots")
def api_slots():
    return jsonify(get_slots())


@app.route("/health")
def health():
    """Always 200 so hosting health checks don't kill the app while the model loads."""
    age = None if producer.last_frame_time is None else round(time.time() - producer.last_frame_time, 1)
    ok = producer.is_alive() and producer.video_open and age is not None and age < 10
    return jsonify(status="ok" if ok else "starting_or_degraded",
                   video_open=producer.video_open,
                   seconds_since_last_frame=age,
                   detections_run=producer.detections_run,
                   slots_loaded=producer.slot_count,
                   last_error=producer.last_error)


if __name__ == "__main__":
    # debug=False / no reloader: the reloader would start a second video thread
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False, threaded=True)
