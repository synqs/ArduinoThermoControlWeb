from flask import Flask
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import eventlet

import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

eventlet.monkey_patch()

# where should I move this normally ?
async_mode = None

bootstrap = Bootstrap();
db = SQLAlchemy();
migrate = Migrate();
socketio = SocketIO();

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    bootstrap.init_app(app);

    # set up the database
    db.init_app(app);
    migrate.init_app(app, db);
    socketio.init_app(app, async_mode='eventlet');

    # import all the components of the app

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.cameracontrol import bp as camera_bp
    app.register_blueprint(camera_bp)

    from app.thermocontrol import bp as thermocontrol_bp
    app.register_blueprint(thermocontrol_bp)

    from app.serialmonitor import bp as serialmonitor_bp
    app.register_blueprint(serialmonitor_bp)

    if not app.debug:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='DeviceControl Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/devicecontrol.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('DeviceControl startup')

    return app
