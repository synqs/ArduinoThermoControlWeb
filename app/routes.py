from app import app, socketio
from app.forms import UpdateForm, DataForm, DisconnectForm, ConnectForm
import serial
import h5py
from threading import Lock
from flask import render_template, flash, redirect, url_for, session
from flask_socketio import emit, disconnect

# for subplots
import numpy as np
from datetime import datetime

thread = None
thread_lock = Lock()

ser = serial.Serial()
#create the dummy dataframed
fname = '';

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    '''
    The main function for rendering the principal site.
    '''
    global ser;
    is_open = ser.is_open;
    return render_template('index.html', async_mode=socketio.async_mode, is_open = is_open)

@app.route('/config', methods=['GET', 'POST'])
def config():
    port = app.config['SERIAL_PORT']
    uform = UpdateForm()
    dform = DisconnectForm()
    cform = ConnectForm()
    global ser;
    is_open = ser.is_open;
    if uform.validate_on_submit():
        #Update the port.
        n_port =  uform.serial_port.data;
        try:
            ser.close()
            ser = serial.Serial(n_port, 9600, timeout = 1)
            if ser.is_open:
                app.config['SERIAL_PORT'] = n_port;
                socketio.emit('connect', namespace='/test')
                flash('We set the serial port to {}'.format(app.config['SERIAL_PORT']))
                return redirect(url_for('index'))
            else:
                 flash('Something went wrong', 'error')
                 return redirect(url_for('config'))
        except Exception as e:
             flash('{}'.format(e), 'error')
             return redirect(url_for('config'))

    if is_open and dform.validate_on_submit():
        #Disconnect the port.
        ser.close()
        is_open = ser.is_open;
        flash('Closed the serial connection')
        return redirect(url_for('config'))
    if cform.validate_on_submit():
        try:
            ser = serial.Serial(app.config['SERIAL_PORT'], 9600, timeout = 1)
            is_open = ser.is_open;
            flash('Opened the serial connection')
            socketio.emit('connect', namespace='/test')
            return redirect(url_for('config'))
        except Exception as e:
             flash('{}'.format(e), 'error')
             return redirect(url_for('config'))
    return render_template('config.html', port = port, form=uform,
        is_open= is_open, dform = dform, cform = cform)

@app.route('/file/<filename>')
def file(filename):
    '''function to save the values of the hdf5 file'''

    # We should add the latest value of the database here. Better would be to trigger the readout.
    # Let us see how this actually works.
    vals = [1, 2, 3];
    with h5py.File(filename, "a") as f:
        if 'globals' in f.keys():
            params = f['globals']
            params.attrs['T_Verr'] = vals[0]
            params.attrs['T_Vmeas'] = vals[1]
            params.attrs['T_Vinp'] = vals[2]
            flash('The added vals to the file {}'.format(filename))
        else:
            flash('The file {} did not have the global group yet.'.format(filename), 'error')
    return render_template('file.html', file = filename)

# communication with the websocket
def get_arduino_data():
    '''
    A function to create test data for plotting.
    '''

    global ser;
    ser.flushInput();
    line = ser.readline();
    ard_str = line.decode(encoding='windows-1252');

    timestamp = datetime.utcnow().replace(microsecond=0).isoformat();
    d_str = timestamp + '\t' + ard_str;
    return d_str

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    run = True;
    while run:
        socketio.sleep(10)
        count += 1
        #data_str = create_test_data()
        global ser;
        if ser.is_open:
            try:
                data_str = get_arduino_data()
                socketio.emit('my_response',
                        {'data': data_str, 'count': count},
                      namespace='/test')
            except Exception as e:
                socketio.emit('my_response',
                {'data': '{}'.format(e), 'count': count},
                namespace='/test')
                run = False
        else:
            run = False
            socketio.emit('my_response',
                {'data': 'Port closed please configure one properly', 'count': count},
                namespace='/test')


@socketio.on('connect', namespace='/test')
def test_connect():
    '''
    we are connecting the client to the server. This will only work if the
    Arduino already has a serial connection
    '''
    global thread
    global ser
    if not ser.is_open:
        flash('Open the serial port first', 'error')
        return
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)
        else:
            if not thread.is_alive():
                thread = None
                emit('connect', namespace='/test')
                return
    emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')

@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    Vinp = np.random.randint(50);
    emit('my_response',
         {'data': Vinp, 'count': session['receive_count']})

# error handling
@app.errorhandler(500)
def internal_error(error):
    flash('An error occured {}'.format(error), 'error')
    return render_template('500.html'), 500

@socketio.on_error_default
def default_error_handler(e):
    print(request.event["message"]) # "my error event"
    print(request.event["args"])    # (data,)
