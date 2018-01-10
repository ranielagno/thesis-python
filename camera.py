from flask_socketio import Namespace, emit, disconnect

frame = None
class Camera(Namespace):
    def on_connect(self):
        print("Camera Connected")
        emit("video_feed")

    def on_disconnect(self):
        print("Camera Disconnected")

    def on_camera(self, picture):
        global frame
        frame = picture

def getFrame():
    return frame
