from flask_restful import Resource
from commands import Commands


class Drone(Resource):

    def get(self,command):    
        self.commands = Commands()
        vehicle = self.commands.getVehicleParams()
        return vehicle
        
    def post(self,command):
        if command is "land":
            self.commands.land()
        elif command is "rtl":
            self.commands.returnToLand()
        elif command is "takeoff":
            data = request.get_json()
            print data
            self.commands.takeOff(data)
        elif command is "route":
            data = request.get_json()
            print data
            self.commands.setMission(data)        
        