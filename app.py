from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2

from detection import process_frame
from analytics import get_stats, update_stats

app = Flask(__name__)
CORS(app)

VIDEO_PATH = "parking.mp4"
camera     = cv2.VideoCapture(VIDEO_PATH)


def generate_frames():
    global camera
    while True:
        success, frame = camera.read()

        # Loop video when it ends
        if not success:
            camera.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, frame = camera.read()
            if not success:
                # Re-open if set() didn't work (some codecs)
                camera.release()
                camera = cv2.VideoCapture(VIDEO_PATH)
                continue

        frame, slot_data = process_frame(frame)
        update_stats(slot_data)

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/stats')
def api_stats():
    return jsonify(get_stats())


if __name__ == "__main__":
    app.run(debug=True)
