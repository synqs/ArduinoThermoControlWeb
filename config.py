import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # ...
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'amTestKey'


    # config of the serial ports
    SERIAL_PORT = '/dev/cu.usbmodem1421'
    SERIAL_TIME = 3;

    # config of the hdf5 file exchange
    REMOTE_FILE = 'Test'

    # config of the camera stuff
    CAMERA_FOLDER = basedir
