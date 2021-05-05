from flask.app import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from .utils.LoggerWrapper import log_setup
from typing import Tuple


def app_setup(app: Flask) -> Tuple[Flask, SocketIO]:
    log_setup()
    CORS(app)
    socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
    return app, socketio
