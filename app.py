from flask import Flask, render_template
from flask_restful import Resource, Api
from flask_socketio import SocketIO, emit
from drone import Drone

app = Flask(__name__)
api = Api(app)
socketio = SocketIO(app)
api.add_resource(Drone, '/drone/<string:command>')
#socketio.on_namespace(Camera('/camera'))

@app.route('/camera')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + getFrame() + b'\r\n',
                mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
