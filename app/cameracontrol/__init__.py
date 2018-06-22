from flask import Blueprint

bp = Blueprint('cameracontrol', __name__, template_folder='templates')

from app.cameracontrol import handlers
