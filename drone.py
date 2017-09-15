from flask import request, copy_current_request_context
from flask_restful import Resource
from flask_socketio import Namespace, emit, socketio
from commands import Commands
from threading import Lock

import json
import time

thread = None
thread_lock = Lock()

class Drone(Resource):
    commands = None

    def get(self,command):
        global commands
        commands = Commands()
        self.vehicle = commands.setup()
        return self.vehicle

    def post(self,command):
        global commands
        if command == "land":
            commands.land()
        elif command == "rtl":
            commands.returnToLand()
        elif command == "takeoff":
            data = request.get_json()
            print data
            commands.takeOff(data['altitude'])
        elif command == "route":
            data = request.get_json()
            print data
            commands.setMission(data)

    @staticmethod
    def returnCommand():
        global commands
        return commands


class DroneParams(Namespace):
    socketio = None
    def __init__(self,*args):
        global socketio
        super(DroneParams, self).__init__(args[0])
        socketio = args[1]

    def on_connect(self):
        global thread
        global socketio
        print "Connected"

        @copy_current_request_context
        def getParamsTask():
            while 1:
                print "Emitting..."
                emit("paramaters", Drone().returnCommand().getVehicleParams())
                socketio.sleep(1)
        with thread_lock:
            if thread is None:
                thread = socketio.start_background_task(target=getParamsTask)
