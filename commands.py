from dronekit import connect, VehicleMode, LocationGlobalRelative, Command
from flask import copy_current_request_context
from pymavlink import mavutil
import config
import time
import math
import argparse
import eventlet

class Commands():

    vehicle = None

    def setup(self):

        parser = argparse.ArgumentParser()
        parser.add_argument('--connect', default=config.connection_string)
        args = parser.parse_args()

        # Connect to the Vehicle
        print 'Connecting to vehicle on: %s' % args.connect
        self.vehicle = connect(args.connect, baud=115200, wait_ready=True)

        print "Basic pre-arm checks"

        """
        # Don't let the user try to arm until autopilot is ready
        while not self.vehicle.is_armable:
            print " Waiting for vehicle to initialise..."
            time.sleep(1)
        """

        self.pool = eventlet.GreenPool(1)

        return self.vehicle

    def getVehicle(self):
        return self.vehicle

    def getVehicleParams(self):

        #self.printVehicleParams()
        vehicleParams = {
            #Global Location (relative altitude)
            "gps_location": {
                "latitude": self.vehicle.location.global_relative_frame.lat,
                "longitude": self.vehicle.location.global_relative_frame.lon,
                "altitude": self.vehicle.location.global_relative_frame.alt
            },
            "velocity": self.vehicle.velocity,
            "battery": {
                "voltage": self.vehicle.battery.voltage,
                "current": self.vehicle.battery.current,
                "level": self.vehicle.battery.level
            },
            "is_armable": self.vehicle.is_armable,
            "system status": self.vehicle.system_status.state,
            "groundspeed": self.vehicle.groundspeed,
            "airspeed": self.vehicle.airspeed,
            "mode": self.vehicle.mode.name,
            "armed": self.vehicle.armed,
            "heading": self.vehicle.heading
        }

        return vehicleParams

    def arm(self):
        self.vehicle.armed = True
        while not self.vehicle.armed:
            print " Waiting for arming..."
            time.sleep(1)

    def disarm(self):
        self.vehicle.armed = False
        while self.vehicle.armed:
            print " Waiting for disarming..."
            time.sleep(1)
        print "Is vehicle armed?", self.vehicle.armed

    def land(self):
        print("Now let's land")
        self.vehicle.mode = VehicleMode("LAND")
        while not self.vehicle.mode.name is "LAND":
            print "Waiting for land command execution..."
            time.sleep(1)
        print "Mode: ", self.vehicle.mode.name

        # Check that vehicle has reached ground altitude
        while True:
            print " Altitude: ", self.vehicle.location.global_relative_frame.alt
            if self.vehicle.location.global_relative_frame.alt <= 0.0:
                print "Reached ground"
                self.disarm()
                break
            time.sleep(1)

    def returnToLand(self):
        print("Now let's return to land")
        self.vehicle.mode = VehicleMode("RTL")
        while not self.vehicle.mode.name is "RTL":
            print "Waiting for return to land command execution..."
            time.sleep(1)

    def takeOff(self, altitude):
        print "Arming motors"
        # Copter should arm in GUIDED mode
        self.vehicle.mode = VehicleMode("GUIDED")
        self.arm()

        print "Taking off!"
        self.vehicle.simple_takeoff(altitude) # Take off to target altitude

        #@copy_current_request_context
        def monitorTakeOffTask():
            print "Spawning monitorTakeOffTask method"

            # Check that vehicle has reached takeoff altitude
            # -*- coding: utf-8 -*-
            #while self.vehicle.mode not in ("LAND", "RTL"):
            while 1:
                print " Altitude: ", self.vehicle.location.global_relative_frame.alt
                #Break and return from function just below target altitude.
                if self.vehicle.location.global_relative_frame.alt>=altitude*0.95:
                    print "Reached target altitude"
                    break;
                time.sleep(1)
            print("Take off complete")

        #self.pool.spawn_n(monitorTakeOffTask)
        monitorTakeOffTask()

    def printVehicleParams(self):
        print " Global Location (relative altitude): {}".format(
            type(self.vehicle.location.global_relative_frame.lat))
        print " Velocity: %s" % type(self.vehicle.velocity)
        print " Battery: %s" % type(self.vehicle.battery.voltage)
        print " Is Armable?: %s" % type(self.vehicle.is_armable)
        print " System status: %s" % type(self.vehicle.system_status.state)
        print " Groundspeed: %s" % type(self.vehicle.groundspeed)    # settable
        print " Airspeed: %s" % type(self.vehicle.airspeed)    # settable
        print " Mode: %s" % type(self.vehicle.mode.name)    # settable
        print " Armed: %s" % type(self.vehicle.armed)    # settable

    def get_distance_metres(self, aLocation1, aLocation2):
        # Returns the ground distance in metres
        # between two LocationGlobal objects.
        dlat = aLocation2.lat - aLocation1.lat
        dlong = aLocation2.lon - aLocation1.lon
        return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5

    def distance_to_current_waypoint(self):
        """
        Gets distance in metres to the current waypoint.
        It returns None for the first waypoint (Home location).
        """

        if self.nextwaypoint==0:
            return None

        # Commands are zero indexed
        missionitem = self.vehicle.commands[self.nextwaypoint-1]

        lat = missionitem.x
        lon = missionitem.y
        alt = missionitem.z
        targetWaypointLocation = LocationGlobalRelative(lat,lon,alt)
        distancetopoint = self.get_distance_metres(
            self.vehicle.location.global_frame, targetWaypointLocation)
        return distancetopoint

    def setMission(self, data):
        # Get the set of commands from the vehicle
        self.cmds = self.vehicle.commands
        print " Clear any existing commands"
        self.cmds.clear()

        print " Define/add new commands."
        # Add new commands.
        #The meaning/order of the parameters is documented in the Command class.

        print "Airspeed: ", data['airspeed']
        self.cmds.add(
            Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, 0, 0, 0, data['airspeed'],
            0, 0, 0, 0, 0))

        for coords in data[u'points']:
            # Create and add commands
            self.cmd = Command(
                0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0,
                coords[u'latitude'], coords[u'longitude'], data['altitude'])
            self.cmds.add(self.cmd)

        self.cmds.add(self.cmd)

        print " Upload new commands to vehicle"
        self.cmds.upload()

        # Start to takeoff
        self.takeOff(data['altitude'])

        print "Starting mission"

        # Reset mission set to first (0) waypoint
        self.vehicle.commands.next=0

        # Set mode to AUTO to start mission
        self.vehicle.mode = VehicleMode("AUTO")

        while not self.vehicle.mode.name == "AUTO":
            print "Waiting for AUTO mode"
            time.sleep(1)

        #@copy_current_request_context
        def monitorMissionTask():
            print "Spawning monitorMissionTask method"

            while 1:
                self.nextwaypoint = self.vehicle.commands.next
                print 'Distance to waypoint (%s): %s' % (self.nextwaypoint,
                 self.distance_to_current_waypoint())

                # Dummy waypoint - as soon as we reach waypoint 4
                # this is true and we exit.

                if self.nextwaypoint > len(data['points']):
                    print "Exit 'standard' mission when start",
                    print "heading to final waypoint %s" % self.nextwaypoint
                    break;

                time.sleep(1)

            #if self.vehicle.mode is "AUTO":
            print "Commencing drone return to landing..."
            self.returnToLand()
            """
            else:
                self.cmds.clear()
                self.cmds.upload()
            """

        #self.pool.spawn_n(monitorMissionTask)
        monitorMissionTask()
