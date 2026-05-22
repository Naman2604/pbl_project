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
    while True:
        success, frame = camera.read()
        if not success:
            # Loop video back to start instead of breaking
            camera.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame, slot_data = process_frame(frame)
        update_stats(slot_data)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/stats')
def api_stats():
    return jsonify(get_stats())


if __name__ == "__main__":
    app.run(debug=True)
