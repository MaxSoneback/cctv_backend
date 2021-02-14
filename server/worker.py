import base64
import threading


class Worker:
    def __init__(self, socket, sid, camera):
        self.socket = socket
        self.sid = sid
        self.camera = camera
        self.thread = None
        self.is_running = True
        self._stop = threading.Event()

    def start(self):
        while self.is_running:
            try:
                success, frame = self.camera.get_frame()
                frame = base64.b64encode(frame.tobytes()).decode('utf-8')
                self.socket.emit('live_feed', {"base64_frame": frame}, room=self.sid)
                self.socket.sleep(0)
            except Exception as e:
                print(e)
        print("Stopped")

    def set_tread(self, thread):
        self.thread = thread

    def stop(self):
        self.is_running = False
