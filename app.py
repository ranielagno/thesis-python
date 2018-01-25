import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_restful import Resource, Api
from flask_socketio import SocketIO, emit
from resources import Drone, Status

import RPi.GPIO as GPIO

app = Flask(__name__)
api = Api(app)
socketio = SocketIO(app, async_mode='eventlet')
api.add_resource(Drone, '/drone/<string:command>')
socketio.on_namespace(Status('/drone'))

@app.route('/camera')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    GPIO.cleanup()
