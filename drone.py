from flask import request
from flask_restful import Resource
from commands import Commands


class Drone(Resource):

    def get(self,command):    
        print "Yeah"
        self.commands = Commands()
        vehicle = self.commands.getVehicleParams()
        return vehicle
        
    def post(self,command):
        self.commands = Commands()
        if command == "land":
            self.commands.land()
        elif command == "rtl":
            self.commands.returnToLand()
        elif command == "takeoff":
            #data = request.get_json()
            #print data
            self.commands.takeOff(2)
        elif command == "route":
            data = request.get_json()
            print data
            self.commands.setMission(data)
        
