from flask import Blueprint

bp = Blueprint('thermocontrol', __name__, template_folder='templates')

from app.thermocontrol import handlers
