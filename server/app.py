import eventlet
eventlet.monkey_patch()

from flask import Flask, request
from flask_socketio import SocketIO
from image_analysis.video_feed import VideoCamera
from worker import Worker
import credentials

app = Flask(__name__)
app.config['SECRET_KEY'] = credentials.SECRET_KEY
io = SocketIO(app,
              path='/backend/socket.io',
              cors_allowed_origins="*",
              async_mode='eventlet')
camera = VideoCamera()
worker_dict = {}


@io.on('connect')
def connect():
    print(f'{request.sid} connected')
    io.emit('connected', {'data': 'Connected'})


@io.on('disconnect')
def disconnect():
    global worker_dict
    worker = worker_dict.pop(request.sid, None)
    if worker is not None:
        worker.stop()
        worker.thread.join()
        if len(worker_dict) == 0:
            camera.close()
    print(f'{request.sid} Disconnected with WebSocket,\n{len(worker_dict)} streams still running')


@io.on('start_feed')
def start_feed():
    if not camera.is_opened():
        camera.open()
    worker = Worker(io, request.sid, camera)
    global worker_dict
    # There is some bug calling this function twice, this if-statement makes sure
    # we don't run unnecessary threads
    if request.sid not in worker_dict:
        worker_dict[request.sid] = worker
        thread = io.start_background_task(target=worker.start)
        worker.set_tread(thread)


if __name__ == '__main__':
    io.run(app, host='0.0.0.0', port=5000)
