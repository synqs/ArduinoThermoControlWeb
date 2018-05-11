from flask import Flask
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from config import Config

# where should I move this normally ?
async_mode = None

app = Flask(__name__)
bootstrap = Bootstrap(app)
socketio = SocketIO(app, async_mode=async_mode)

app.config.from_object(Config)

from app import routes
