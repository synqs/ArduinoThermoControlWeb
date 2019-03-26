from app import socketio, db
from app.main import bp

from app.main.forms import LoginForm
from app.main.models import User

from app.thermocontrol.models import TempControl, WebTempControl
from app.serialmonitor.models import ArduinoSerial
from app.cameracontrol.models import Camera

from flask import render_template, flash, redirect, url_for, session
from flask_socketio import emit, disconnect

from flask_login import current_user, login_user

@bp.route('/')
@bp.route('/index', methods=['GET', 'POST'])
def index():
    '''
    The main function for rendering the principal site.
    '''

    tcontrols = TempControl.query.all();
    n_tcs = len(tcontrols);

    wtcontrols = WebTempControl.query.all();
    n_wtcs = len(wtcontrols);

    smonitors = ArduinoSerial.query.all();
    n_sm = len(smonitors);

    cams = Camera.query.all();
    n_cameras = len(cams);

    return render_template('index.html',n_tcs = n_tcs, tempcontrols = tcontrols,
    n_wtcs = n_wtcs, wtempcontrols = wtcontrols, n_sm = n_sm, serialmonitors = smonitors, n_cameras = n_cameras, cameras = cams);

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.index'))
    return render_template('login.html', title='Sign In', form=form)

# communication with the websocket
@socketio.on('connect')
def run_connect():
    '''
    we are connecting the client to the server. This will only work if the
    Arduino already has a serial connection
    '''
    socketio.emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('my_ping')
def ping_pong():
    emit('my_pong')
