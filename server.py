from flask import Flask, Response, request, jsonify
from camera_opencv import Camera
from ai import get_encodings, process_image
from storage import Storage
from requester import get_user_data
from utils import decode_image, encode_encoding
import threading


app = Flask(__name__)


def gen(camera):
    # Video streaming generator function.
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/feed')
def video_feed():
    # Video streaming route. Put this in the src attribute of an img tag.
    return Response(gen(Camera()), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/encode', methods=['POST'])
def encode():
    data = request.json
    if data['image'] and len(data['image']) > 0:
        image = decode_image(data['image'])
        processed = process_image(image)

        encodings = get_encodings(processed)

        if len(encodings) > 0:
            encoded = encode_encoding(encodings[0])
            return jsonify({
                'success': 'true',
                'message': 'generated encoding',
                'encoding': encoded})

    return jsonify({'success': 'false', 'message': 'Ivalid data!'})


def update_faces():
    threading.Timer(5.0, update_faces).start()
    user_data = get_user_data()
    Storage.set_encodings(user_data['encodings'])
    Storage.set_names(user_data['names'])
    print('updated')


if __name__ == '__main__':
    update_faces()
    gen(Camera())

    app.run(host='localhost', threaded=True)
