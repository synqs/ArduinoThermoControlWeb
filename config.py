import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # ...
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'amTestKey'
    SERIAL_PORT = '/dev/cu.usbmodem1421'
    SERIAL_TIME = 3;
    REMOTE_FILE = 'Test'
