from flask import Flask, request, copy_current_request_context
from flask_restful import Resource, Api
from flask_socketio import SocketIO, emit
from drone import Drone, DroneParams
from threading import Lock

app = Flask(__name__)
api = Api(app)
socketio = SocketIO(app)
#thread = None
#thread_lock = Lock()
#drone = Drone()
api.add_resource(Drone, '/drone/<string:command>')
socketio.on_namespace(DroneParams('/drone', socketio))
"""
@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    print e

@socketio.on('hello', namespace='/drone')
def hello(message):
    print message
    emit("paramaters", "hello", callback=ack)

@socketio.on('connect', namespace='/drone')
def on_connect():
    global thread
    print "Connected"
    @copy_current_request_context
    def getParamsTask():
        while 1:
            emit("paramaters", Drone().returnCommand().getVehicleParams())
            socketio.sleep(10)
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=getParamsTask)
"""
def ack():
    print 'message was received!'
"""
def signal_handler(signal, frame):
    print "Now landing!!"
    drone.emergencyLand()
    sys.exit(0)
"""

#signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0', threaded=True)
    socketio.run(app, host='0.0.0.0', port=5000)
