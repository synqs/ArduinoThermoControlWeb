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

# import all the components of the app

from app.main import bp as main_bp
app.register_blueprint(main_bp)

from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from app.thermocontrol import bp as thermocontrol_bp
app.register_blueprint(thermocontrol_bp)

from app.serialmonitor import bp as serialmonitor_bp
app.register_blueprint(serialmonitor_bp)
