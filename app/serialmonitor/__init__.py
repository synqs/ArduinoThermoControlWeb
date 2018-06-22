from flask import Blueprint

bp = Blueprint('serialmonitor', __name__, template_folder='templates')

from app.serialmonitor import handlers
