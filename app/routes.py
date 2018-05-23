from app import app, socketio
from app.forms import UpdateForm, DataForm, DisconnectForm, ConnectForm
import serial
import h5py
from threading import Lock
from flask import render_template, flash, redirect, url_for, session

import time

from flask_socketio import emit, disconnect
import eventlet

# for subplots
import numpy as np
from datetime import datetime

thread = None
workerObject= None
thread_lock = Lock()
ssProto = None

#create the dummy dataframe
fname = '';

class SerialSocketProtocol(object):
    '''
    A class which combines the serial connection and the socket into a single
    class, such that we can handle these things more properly.
    '''

    serial = None
    switch = False
    unit_of_work = 0

    def __init__(self, socketio):
        """
        assign socketio object to emit
        """
        self.serial = serial.Serial()
        self.switch = False
        self.socketio = socketio

    def is_open(self):
        '''
        test if the serial connection is open
        '''
        return self.serial.is_open

    def is_alive(self):
        """
        return the running status
        """
        return self.switch

    def stop(self):
        """
        stop the loop and later also the serial port
        """
        self.switch = False

    def start(self):
        """
        stop the loop and later also the serial port
        """
        self.switch = True

    def do_work(self):
        """
        do work and emit message
        """

        while self.switch:
            self.unit_of_work += 1

            # must call emit from the socket io
            # must specify the namespace
            global ssProto;
            ser = ssProto.serial;

            if ser.is_open:
                try:
                    data_str = get_arduino_data()
                    self.socketio.emit('my_response',
                    {'data': data_str, 'count': self.unit_of_work})
                except Exception as e:
                    self.socketio.emit('my_response',
                    {'data': '{}'.format(e), 'count': self.unit_of_work})
                    self.switch = False
            else:
                self.switch = False
                # TODO: Make this a link
                error_str = 'Port closed. please configure one properly under config.'
                self.socketio.emit('my_response',
                {'data': error_str, 'count': self.unit_of_work})

                # important to use eventlet's sleep method
                eventlet.sleep(1)


ssProto = SerialSocketProtocol(socketio)

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    '''
    The main function for rendering the principal site.
    '''
    global thread;
    global ssProto
    is_open = ssProto.is_open();
    is_alive = ssProto.is_alive();

    dform = DisconnectForm();

    socketio.emit('connect')
    return render_template('index.html', dform = dform, async_mode=socketio.async_mode, is_open = is_open, is_alive = is_alive)

@app.route('/config')
def config():
    port = app.config['SERIAL_PORT']
    uform = UpdateForm()
    dform = DisconnectForm()
    cform = ConnectForm()

    global ssProto;

    is_open = ssProto.is_open();
    is_alive = ssProto.is_alive();

    return render_template('config.html', port = port, form=uform,
        is_open= is_open, is_alive = is_alive, dform = dform, cform = cform)

@app.route('/start', methods=['POST'])
def start():

    cform = ConnectForm()

    global thread;
    global ssProto;

    if cform.validate_on_submit():
        try:
            ssProto.serial = serial.Serial(app.config['SERIAL_PORT'], 9600, timeout = 1)

            #TODO: also open the arduino here.
            flash('Opened the serial connection')
            return redirect(url_for('config'))
        except Exception as e:
            flash('{}'.format(e), 'error')
            return redirect(url_for('config'))

    return redirect(url_for('config'))

@app.route('/stop', methods=['POST'])
def stop():
    dform = DisconnectForm()
    global ssProto;

    if dform.validate_on_submit():
        #Disconnect the port.
        ssProto.stop()
        ssProto.serial.close()

        flash('Closed the serial connection')
        return redirect(url_for('config'))

    return redirect(url_for('config'))

@app.route('/update', methods=['POST'])
def update():
    '''
    Update the serial port.
    '''
    uform = UpdateForm()
    global thread;
    global ssProto

    if uform.validate_on_submit():
        n_port =  uform.serial_port.data;
        try:
            ssProto.serial.close()
            ssProto.serial = serial.Serial(n_port, 9600, timeout = 1)
            if ssProto.is_open():
                app.config['SERIAL_PORT'] = n_port;
                socketio.emit('connect')
                flash('We set the serial port to {}'.format(app.config['SERIAL_PORT']))
                return redirect(url_for('config'))
            else:
                 flash('Something went wrong', 'error')
                 return redirect(url_for('config'))
        except Exception as e:
             flash('{}'.format(e), 'error')
             return redirect(url_for('config'))

    return redirect(url_for('config'))

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

    global ssProto;
    ser = ssProto.serial;
    ser.flushInput();
    line = ser.readline();
    ard_str = line.decode(encoding='windows-1252');

    timestamp = datetime.utcnow().replace(microsecond=0).isoformat();
    d_str = timestamp + '\t' + ard_str;
    return d_str

@socketio.on('connect')
def run_connect():
    '''
    we are connecting the client to the server. This will only work if the
    Arduino already has a serial connection
    '''
    print('Connecting the websocket')
    global thread
    global ssProto;
    ser = ssProto.serial;

    if not ser.is_open:
         flash('Open the serial port first', 'error')
         return
    with thread_lock:
         if thread is None:
             ssProto.start();
             thread = socketio.start_background_task(target=ssProto.do_work)
             print('Start the background task')
         else:

             print('Thread already exists')
             if not thread.is_alive():
                 thread = None
                 emit('connect')
                 return
    socketio.emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('stop')
def run_disconnect():
    print('Should disconnect')
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
        {'data': 'Disconnected!', 'count': session['receive_count']})
    global ssProto;
    ser = ssProto.serial;

    if  ser.is_open:
        ser.close();

    ssProto.stop()
    disconnect()

@socketio.on('join')
def run_join():
    print('Should join')
    global thread
    with thread_lock:
        print('Connecting the websocket')
        if thread is None:
             thread = socketio.start_background_task(target=ssProto.do_work)
             print('Start the background task')
        else:

             print('Thread already exists')
             if not thread.is_alive():
                 thread = None
                 emit('connect')
                 return
    socketio.emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('my_ping')
def ping_pong():
    emit('my_pong')

# error handling
@app.errorhandler(500)
def internal_error(error):
    flash('An error occured {}'.format(error), 'error')
    return render_template('500.html'), 500
