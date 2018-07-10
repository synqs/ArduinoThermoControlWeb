from app import app, socketio, db
from app.main import bp
from app.thermocontrol.models import TempControl
from app.serialmonitor.models import serialmonitors, ArduinoSerial
from app.cameracontrol.models import Camera

import h5py
import git
import numpy as np

from flask import render_template, flash, redirect, url_for, session
from flask_socketio import emit, disconnect

# for subplots
import numpy as np
import threading

@app.context_processor
def git_url():
    '''
    The main function for rendering the principal site.
    '''
    repo = git.Repo(search_parent_directories=True)
    add =repo.remote().url
    add_c = add.split('.git')[0];
    comm = repo.head.object.hexsha;

    commit_url = add_c + '/tree/' + comm;
    issues_url = add_c + '/issues';

    return dict(git_url = commit_url, issues_url = issues_url);

@bp.route('/')
@bp.route('/index', methods=['GET', 'POST'])
def index():
    '''
    The main function for rendering the principal site.
    '''

    tcontrols = TempControl.query.all();
    n_tcs = len(tcontrols);

    smonitors = ArduinoSerial.query.all();
    n_sm = len(smonitors);

    cams = Camera.query.all();
    n_cameras = len(cams);

    return render_template('index.html',n_tcs = n_tcs, tempcontrols = tcontrols,
    n_sm = n_sm, serialmonitors = smonitors, n_cameras = n_cameras, cameras = cams);

@bp.route('/file/<filestring>')
def file(filestring):
    '''function to save the values of the hdf5 file. It should have the following structure
    <ard_nr>+<filename>
    '''
    # first let us devide into the right parts
    print(filestring)
    parts = filestring.split('+');
    if not len(parts) == 2:
        flash('The filestring should be of the form')
        return redirect(url_for('index'))

    filename = parts[1]
    id = int(parts[0])

    global tempcontrols;

    if id >= len(tempcontrols):
        flash('Arduino Index out of range.')
        return redirect(url_for('index'))

    arduino = tempcontrols[id];
    # We should add the latest value of the database here. Better would be to trigger the readout.
    # Let us see how this actually works.
    vals = arduino.ard_str.split(',');
    if vals:
        with h5py.File(filename, "a") as f:
            if 'globals' in f.keys():
                params = f['globals']
                params.attrs['TSet'] = np.float(vals[0])
                params.attrs['TMeasure'] = np.float(vals[1])
                flash('Added the vals {} to the file {}'.format(arduino.ard_str, filename))
            else:
                flash('The file {} did not have the global group yet.'.format(filename), 'error')
    else:
        flash('Did not have any values to save', 'error')

    return render_template('file.html', file = filename, vals = vals)

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
