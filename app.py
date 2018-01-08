from flask import Flask, request, copy_current_request_context
from flask_restful import Resource, Api
from flask_socketio import SocketIO, emit
from drone import Drone
#from threading import Lock
#import eventlet

#eventlet.monkey_patch()

#async_mode = "eventlet"
app = Flask(__name__)
api = Api(app)
socketio = SocketIO(app)
api.add_resource(Drone, '/drone/<string:command>')
#socketio.on_namespace(DroneParams('/drone', socketio))

if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0', port=5005)
    socketio.run(app, host='0.0.0.0', port=5005, debug=True)
