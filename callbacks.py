from flask_socketio import emit

class Callbacks():

    def __init__(self, *args):

        self.last_latitude = 0.0
        self.last_longitude = 0.0
        self.last_altitude = 0.0
        self.last_current = 0.0
        self.last_voltage = 0.0
        self.last_heading = 0
        self.last_level = 0
        vehicle = args[0]

        vehicle.add_attribute_listener('location.global_relative_frame',
            self.location_callback)
        vehicle.add_attribute_listener('heading', self.heading_callback)
        vehicle.add_attribute_listener('battery', self.battery_callback)
        vehicle.add_attribute_listener('mode', self.mode_callback)

    def location_callback(self, *args):
        value = args[len(args) - 1]
        if round(value.lat, 6) != round(self.last_latitude, 6):
            self.last_latitude = value.lat
            print "Latitude: ", value.lat, "\n"
            emit("latitude", value.lat)
        if round(value.lon, 6) != round(self.last_longitude, 6):
            self.last_longitude = value.lon
            print "Longitude: ", value.lon, "\n"
            emit("longitude", value.lon)
        if round(value.alt) != round(self.last_altitude):
            self.last_altitude = value.alt
            print "Altitude: ", value.alt, "\n"
            emit("altitude", value.alt)

    def heading_callback(self, *args):
        value = args[len(args) - 1]
        if value != self.last_heading:
            self.last_heading = value
            print "heading ", value, "\n"
            emit("heading", value)

    def battery_callback(self, *args):
        value = args[len(args) - 1]
        if round(value.current) != round(self.last_current):
            self.last_current = value.current
            print "current ", value.current, "\n"
        if round(value.voltage) != round(self.last_voltage):
            self.last_voltage = value.voltage
            print "voltage ", value.voltage, "\n"
        if value.level != self.last_level:
            self.last_level = value.level
            print "level ", value.level, "\n"

    def mode_callback(self, *args):
        value = args[len(args) - 1]
        print "mode ", value, "\n"
