from app import app, socketio
from app.forms import UpdateForm, DataForm, DisconnectForm, ConnectForm
import serial
import h5py
from flask import render_template, flash, redirect, url_for, session

import time

from flask_socketio import emit, disconnect
import eventlet

# for subplots
import numpy as np
from datetime import datetime

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

    def connection_open(self):
        '''
        Is the protocol running ?
        '''
        return self.is_alive() and self.is_open()

    def stop(self):
        """
        stop the loop and later also the serial port
        """
        self.switch = False

    def start(self):
        """
        stop the loop and later also the serial port
        """
        if not self.switch:
            if not self.is_open():
                print('the serial port should be open right now')
            else:
                self.switch = True
                thread = self.socketio.start_background_task(target=self.do_work)
                print('Started')
        else:
            print('Already running')

    def open_serial(self, port, baud_rate, timeout = 1):
        """
        stop the loop and later also the serial port
        """
        if self.is_open():
            print('Already open')
            self.serial.close()
        else:
            print('Open it')
        self.serial = serial.Serial(port, 9600, timeout = 1)

    def do_work(self):
        """
        do work and emit message
        """

        while self.switch:
            self.unit_of_work += 1

            # must call emit from the socketio
            # must specify the namespace

            if self.is_open():
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
            eventlet.sleep(3)


ssProto = SerialSocketProtocol(socketio)

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    '''
    The main function for rendering the principal site.
    '''
    global ssProto
    conn_open = ssProto.connection_open()
    dform = DisconnectForm();
    return render_template('index.html', dform = dform, async_mode=socketio.async_mode, conn_open = conn_open)

@app.route('/config')
def config():
    port = app.config['SERIAL_PORT']
    uform = UpdateForm()
    dform = DisconnectForm()
    cform = ConnectForm()

    global ssProto;
    conn_open = ssProto.connection_open()

    return render_template('config.html', port = port, form=uform, dform = dform,
        cform = cform, conn_open = conn_open)

@app.route('/start', methods=['POST'])
def start():

    cform = ConnectForm()

    global ssProto;

    if cform.validate_on_submit():
        try:
            ssProto.open_serial(app.config['SERIAL_PORT'], 9600, timeout = 1)
            ssProto.start()
            flash('Started the connection')
            return redirect(url_for('index'))
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
    global ssProto

    if uform.validate_on_submit():
        n_port =  uform.serial_port.data;
        try:

            ssProto.open_serial(n_port, 9600, timeout = 1)
            ssProto.start()
            if ssProto.is_open():
                app.config['SERIAL_PORT'] = n_port;
                flash('We set the serial port to {}'.format(app.config['SERIAL_PORT']))
                return redirect(url_for('index'))
            else:
                 flash('Update of the serial port went wrong', 'error')
                 return redirect(url_for('config'))
        except Exception as e:
             flash('{}'.format(e), 'error')
             return redirect(url_for('config'))
    else:
        flash('Update of the serial port went wrong', 'error')
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
    # how do we only read the very last line ?
    # TODO: I am pretty sure that the flushInput is a real noise source
    #ser.flushInput();
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
    socketio.emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('stop')
def run_disconnect():
    print('Should disconnect')
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
        {'data': 'Disconnected!', 'count': session['receive_count']})
    global ssProto;
    ser = ssProto.serial;
    ser.close();
    ssProto.stop();

@socketio.on('join')
def run_join():
    print('Should join')
    global ssProto;
    ssProto.start();

    socketio.emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('my_ping')
def ping_pong():
    emit('my_pong')

# error handling
@app.errorhandler(500)
def internal_error(error):
    flash('An error occured {}'.format(error), 'error')
    return render_template('500.html'), 500
