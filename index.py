import io
from picamera2 import Picamera2
from flask import Flask, Response
from threading import Thread
import os

app = Flask(__name__)

# http://127.0.0.1:5000/video_feed

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"}))
picam2.set_controls({"FrameDurationLimits": (33333, 33333)})  # approximately 30 fps
picam2.start()

def generate_frames():
    while True:
        stream = io.BytesIO()
        picam2.capture_file(stream, format='jpeg')
        stream.seek(0)
        frame = stream.read()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Get the port from the environment variables
    thread = Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': port, 'threaded': True})
    thread.start()

