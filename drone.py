from flask import request
from flask_restful import Resource
import json
from commands import Commands


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
