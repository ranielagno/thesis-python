from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
import time
import argparse  

class Commands():

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--connect', default='/dev/serial0')
        args = parser.parse_args()

        # Connect to the Vehicle
        print 'Connecting to vehicle on: %s' % args.connect
        self.vehicle = connect(args.connect, baud=57600, wait_ready=True)
        
        print "Basic pre-arm checks"
        
        # Timeout 5 mins
        timeout = time.time() + 60*5
        
        # Don't let the user try to arm until autopilot is ready
        while not self.vehicle.is_armable and time.time() < timeout:
            print " Waiting for vehicle to initialise..."
            time.sleep(1)
            
    def getVehicleParams(self):
        vehicleParams = {
            "Global Location": self.vehicle.location.global_frame,
            "Global Location (relative altitude)": self.vehicle.location.global_relative_frame,
            "Local Location": self.vehicle.location.local_frame,
            "Attitude": self.vehicle.attitude,
            "Velocity": self.vehicle.velocity,
            "GPS": self.vehicle.gps_0,
            "Battery": self.vehicle.battery,
            "Is Armable?": self.vehicle.is_armable,
            "System status": self.vehicle.system_status.state,
            "Groundspeed": self.vehicle.groundspeed,
            "Airspeed": self.vehicle.airspeed,
            "Mode": self.vehicle.mode.name,
            "Armed": self.vehicle.armed
        }
        self.printVehicleParams()
        if not self.vehicle.is_armable:
            return {"message": "Error! Drone can't initialise!"}
        return vehicleParams
        
    def arm(self):
        self.vehicle.armed   = True
        while not vehicle.armed:
            print " Waiting for arming..."
            time.sleep(1)
        
    def disarm(self):
        self.vehicle.armed   = False
        while vehicle.armed:
            print " Waiting for disarming..."
            time.sleep(1)
        
    def land(self):
        print("Now let's land")
        vehicle.mode = VehicleMode("LAND")
        while not self.vehicle.mode.name is "LAND":     
            print " Waiting for land command execution..."
            time.sleep(1)
        
    def returnToLand(self):
        print("Now let's return to land")
        vehicle.mode = VehicleMode("RTL")
        while not self.vehicle.mode.name is "RTL":
            print " Waiting for return to land command execution..."
            time.sleep(1)
        
    def takeOff(self, altitude):
        print "Arming motors"
        # Copter should arm in GUIDED mode
        self.vehicle.mode    = VehicleMode("GUIDED")
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
        print("Now change the mode to loiter")
        self.vehicle.mode = VehicleMode("LOITER")
        
    def setMission(self, data):
        pass
        
    def printVehicleParams(self):
        print " Global Location: %s" % self.vehicle.location.global_frame
        print " Global Location (relative altitude): %s" % self.vehicle.location.global_relative_frame
        print " Local Location: %s" % self.vehicle.location.local_frame
        print " Attitude: %s" % self.vehicle.attitude
        print " Velocity: %s" % self.vehicle.velocity
        print " GPS: %s" % self.vehicle.gps_0
        print " Battery: %s" % self.vehicle.battery
        print " Is Armable?: %s" % self.vehicle.is_armable
        print " System status: %s" % self.vehicle.system_status.state
        print " Groundspeed: %s" % self.vehicle.groundspeed    # settable
        print " Airspeed: %s" % self.vehicle.airspeed    # settable
        print " Mode: %s" % self.vehicle.mode.name    # settable
        print " Armed: %s" % self.vehicle.armed    # settable
