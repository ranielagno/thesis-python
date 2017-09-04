from dronekit import connect, VehicleMode, LocationGlobalRelative, Command
from pymavlink import mavutil
import time
import math
import argparse

# For simulator
import dronekit_sitl

class Commands():

    def setup(self):
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('--connect', default='/dev/serial0')
        args = parser.parse_args()

        # Connect to the Vehicle
        print 'Connecting to vehicle on: %s' % args.connect
        self.vehicle = connect(args.connect, baud=57600, wait_ready=True)
        """

        # Connection for simulator
        sitl = dronekit_sitl.start_default()
        connection_string = sitl.connection_string()
        print("Connecting to vehicle on: %s" % (connection_string,))
        self.vehicle = connect(connection_string, wait_ready=True)

        print "Basic pre-arm checks"

        # Timeout 5 mins
        timeout = time.time() + 60*5

        # Don't let the user try to arm until autopilot is ready
        while not self.vehicle.is_armable and time.time() < timeout:
            print " Waiting for vehicle to initialise..."
            time.sleep(1)

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
            "armed": self.vehicle.armed
        }
        self.printVehicleParams()
        if not self.vehicle.is_armable:
            return {"message": "Error! Drone can't initialise!"}
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
        vehicle.mode = VehicleMode("RTL")
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

        # Check that vehicle has reached takeoff altitude
        while True:
            print " Altitude: ", self.vehicle.location.global_relative_frame.alt
            #Break and return from function just below target altitude.
            if self.vehicle.location.global_relative_frame.alt>=altitude*0.95:
                print "Reached target altitude"
                break;
            time.sleep(1)
        print("Take off complete")

    def printVehicleParams(self):
        print " Global Location (relative altitude): {}".format(
            self.vehicle.location.global_relative_frame)
        print " Velocity: %s" % self.vehicle.velocity
        print " Battery: %s" % self.vehicle.battery
        print " Is Armable?: %s" % self.vehicle.is_armable
        print " System status: %s" % self.vehicle.system_status.state
        print " Groundspeed: %s" % self.vehicle.groundspeed    # settable
        print " Airspeed: %s" % self.vehicle.airspeed    # settable
        print " Mode: %s" % self.vehicle.mode.name    # settable
        print " Armed: %s" % self.vehicle.armed    # settable

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
        nextwaypoint = self.vehicle.commands.next
        if nextwaypoint==0:
            return None

        # Commands are zero indexed
        missionitem = self.vehicle.commands[nextwaypoint-1]
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

        #Add MAV_CMD_NAV_TAKEOFF command.
        #This is ignored if the vehicle is already in the air.
        self.cmds.add(
            Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, 10))

        for coords in data[u'points']:
            # Create and add commands
            self.cmd = Command(
                0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0,
                coords[u'latitude'], coords[u'longitude'], data['altitude'])
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

        # Monitor mission.
        # Demonstrates getting and setting the command number
        # Uses distance_to_current_waypoint(),
        # a convenience function for finding the distance to the next waypoint.

        while True:
            nextwaypoint = self.vehicle.commands.next
            print 'Distance to waypoint ({0}): {1:.4f}'.format(
                nextwaypoint, self.distance_to_current_waypoint())

            # Dummy waypoint - as soon as we reach waypoint 4
            # this is true and we exit.
            if nextwaypoint==len(data['points']):
                print "Exit 'standard' mission when start",
                print "heading to final waypoint %s" % len(data['points'])
                break;
            time.sleep(1)

        print 'Return to launch'
        self.vehicle.mode = VehicleMode("RTL")
