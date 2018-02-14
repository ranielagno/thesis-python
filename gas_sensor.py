import time
import eventlet
import random
import config


class GasSensor():

    HIGH_PIN = 16
    INPUT_PIN = 18
    location = []
    vehicle = None

    def __init__(self, vehicle):

        # get vehicle
        self.vehicle = vehicle

        if config.build_type is 'prod':
            import RPi.GPIO as GPIO

            # setup GPIO
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.HIGH_PIN, GPIO.OUT)
            GPIO.setup(self.INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

            # setup pins
            GPIO.add_event_detect(self.INPUT_PIN, GPIO.RISING, callback=self.detectGas)
            GPIO.output(self.HIGH_PIN, GPIO.HIGH)

    # for prod build
    def detectGas(self, pin):

        print "Gas Detected!"
        time.sleep(1)

        # Code for sensing while drone is ACTIVE
        # self.vehicle.system_status.state is "ACTIVE"
        if self.vehicle is not None:

            gps_location = {
                "latitude": self.vehicle.location.global_relative_frame.lat,
                "longitude": self.vehicle.location.global_relative_frame.lon,
                "altitude": self.vehicle.location.global_relative_frame.alt
            }
            self.location.append(gps_location)

    # for dev build
    def testDetectGas(self):
        while 1:

            if self.vehicle is not None and self.vehicle.system_status.state is "ACTIVE":
                gas_reading = random.randint(0, 255)

                if gas_reading > 200:
                    gps_location = {
                        "latitude": self.vehicle.location.global_relative_frame.lat,
                        "longitude": self.vehicle.location.global_relative_frame.lon,
                        "altitude": self.vehicle.location.global_relative_frame.alt
                    }
                    self.location.append(gps_location)
                    print "Gas Detected!!"
                    #emit('gas_detected', gps_location)
            eventlet.sleep(1)
