from flask import request, copy_current_request_context
from flask_restful import Resource
from flask_socketio import Namespace, emit
from commands import Commands
from gas_sensor import GasSensor

import eventlet
import config
import json
import time

commands = Commands()

# initializing entities
vehicle = commands.getVehicle()
gas_sensor = None

# for filtering repeated locations
gas_locations = []


class Drone(Resource):

    def get(self,command):
        global commands
        global vehicle
        global gas_sensor

        if vehicle is None:
            vehicle = commands.setup()
            gas_sensor = GasSensor(vehicle)

            if config.build_type is 'dev':
                eventlet.spawn_n(gas_sensor.testDetectGas)

        return commands.getVehicleParams()

    def post(self,command):
        global commands
        if command == "land":
            commands.land()
        elif command == "rtl":
            commands.returnToLand()
        elif command == "takeoff":
            self.reset_locations()
            data = request.get_json()
            print data
            commands.takeOff(data['altitude'])
        elif command == "route":
            self.reset_locations()
            data = request.get_json()
            print data
            commands.setMission(data)

    def reset_locations(self):
        gas_locations = []


class Status(Namespace):

    def on_connect(self):
        global commands
        global gas_sensor
        global gas_locations

        print "Connected"

        self.is_connected = True

        @copy_current_request_context
        def getStatusTask():
            while self.is_connected:
                emit("parameters", commands.getVehicleParams())
                eventlet.sleep(0.5)

                # for updating the client of gas location
                if gas_sensor and gas_sensor.location:
                    for gps_location in gas_sensor.location:
                        if gps_location not in gas_locations:
                            emit('gas_detected', gps_location)
                            gas_locations.append(gps_location)
                            eventlet.sleep(0.1)
                    gas_sensor.location = []

            print "Get status task finished"

        if commands.getVehicle() is not None:
            eventlet.spawn_n(getStatusTask)

    def on_disconnect(self):

        print "Disconnect"
        self.is_connected = False
