from flask import request, copy_current_request_context
from flask_restful import Resource
from flask_socketio import Namespace, emit, socketio
from commands import Commands
from threading import Lock

import json
import time

thread = None
commands = Commands()
thread_lock = Lock()
vehicle = commands.getVehicle()

class Drone(Resource):

    def get(self,command):
        global commands
        global vehicle
        
        if vehicle is None:     
            vehicle = commands.setup()

        return commands.getVehicleParams()

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


class DroneParams(Namespace):

    socketio = None

    def __init__(self,*args):
        super(DroneParams, self).__init__(args[0])
        self.socketio = args[1]

    def on_connect(self):
        global thread
        global commands

        print "Connected"

        @copy_current_request_context
        def getParamsTask():
            while 1:
                print "Emitting..."
                emit("paramaters", commands.getVehicleParams())
                self.socketio.sleep(1)

        with thread_lock:
            if thread is None:
                thread = self.socketio.start_background_task(target=getParamsTask)
