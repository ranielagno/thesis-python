import RPi.GPIO as GPIO
import eventlet


class GasSensor():
    
    HIGH_PIN = 16
    INPUT_PIN = 18
    location = []
    vehicle = None

    def __init__(self, vehicle):
      
        # get vehicle
        self.vehicle = vehicle
       
        # setup GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.HIGH_PIN, GPIO.OUT)
        GPIO.setup(self.INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # setup pins
        GPIO.add_event_detect(self.INPUT_PIN, GPIO.RISING, callback=self.detectGas)
        GPIO.output(self.HIGH_PIN, GPIO.HIGH)
       
    def detectGas(self, pin):
    
        print "Gas Detected!"
        eventlet.sleep(1)
        
        if self.vehicle is not None and self.vehicle.system_status.state is "ACTIVE":
            
            gps_location = {
                "latitude": vehicle.location.global_relative_frame.lat,
                "longitude": vehicle.location.global_relative_frame.lon,
                "altitude": vehicle.location.global_relative_frame.alt
            }
            self.location.append(gps_location)
       
