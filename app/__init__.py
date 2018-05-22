from flask import Flask
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from config import Config
import eventlet
eventlet.monkey_patch()

# where should I move this normally ?
async_mode = None

app = Flask(__name__)
bootstrap = Bootstrap(app)
socketio = SocketIO(app, async_mode='eventlet')

app.config.from_object(Config)

from app import routes
