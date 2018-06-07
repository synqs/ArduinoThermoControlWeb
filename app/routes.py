from app import app, socketio
from app.forms import UpdateForm, DisconnectForm, ConnectForm, SerialWaitForm
from app.forms import UpdateArduinoForm, UpdateGainForm, UpdateIntegralForm, UpdateDifferentialForm
import serial
import h5py
import git
import numpy as np
from flask import render_template, flash, redirect, url_for, session

import time

from flask_socketio import emit, disconnect
import eventlet

# for subplots
import numpy as np
from datetime import datetime

ssProto = None
ard_str = '';

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
        self.unit_of_work = 0

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
        else:
            print('Already running')

    def open_serial(self, port, baud_rate, timeout = 1):
        """
        open the serial port
        """
        if self.is_open():
            self.serial.close()
        else:
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
                    timestamp, ard_str = get_arduino_data()

                    vals = ard_str.split(',');
                    self.socketio.emit('log_response',
                    {'time':timestamp, 'data': vals, 'count': self.unit_of_work})
                except Exception as e:
                    self.socketio.emit('my_response',
                    {'data': '{}'.format(e), 'count': self.unit_of_work})
                    self.switch = False
            else:
                self.switch = False
                # TODO: Make this a link
                error_str = 'Port closed. please configure one properly under config.'
                self.socketio.emit('log_response',
                {'data': error_str, 'count': self.unit_of_work})

                # important to use eventlet's sleep method
            eventlet.sleep(app.config['SERIAL_TIME'])


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
    return render_template('index.html', dform = dform, conn_open = conn_open)

@app.context_processor
def git_url():
    '''
    The main function for rendering the principal site.
    '''
    repo = git.Repo(search_parent_directories=True)
    add =repo.remote().url
    add_c = add.split('.git')[0];
    comm = repo.head.object.hexsha;
    return dict(git_url = add_c + '/tree/' + comm);


@app.route('/config')
def config():
    port = app.config['SERIAL_PORT']
    dform = DisconnectForm()
    cform = ConnectForm()

    uform = UpdateForm()
    wform = SerialWaitForm()

    arduino_form = UpdateArduinoForm()
    gform = UpdateGainForm()
    iform = UpdateIntegralForm()
    diff_form = UpdateDifferentialForm()

    global ssProto;
    conn_open = ssProto.connection_open()

    return render_template('config.html', port = port, form=uform, dform = dform,
        cform = cform, conn_open = conn_open, arduino_form = arduino_form,
        gform = gform, iform = iform,diff_form = diff_form, wform = wform);

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

@app.route('/arduino', methods=['POST'])
def arduino():
    '''
    Configure now settings for the arduino.
    '''
    aform = UpdateArduinoForm()
    global ssProto

    if aform.validate_on_submit():
        n_setpoint =  aform.setpoint.data;
        if ssProto.is_open():
            o_str = 's{}'.format(n_setpoint)
            b = o_str.encode()
            ssProto.serial.write(b)
            flash('We set the serial port to {}'.format(n_setpoint))
        else:
            flash('Serial port not open.', 'error')
        return redirect(url_for('config'))
    else:
        port = app.config['SERIAL_PORT']

        uform = UpdateForm()

        wform = SerialWaitForm()
        dform = DisconnectForm()
        cform = ConnectForm()
        gform = UpdateGainForm()
        iform = UpdateIntegralForm()
        diff_form = UpdateDifferentialForm()

        conn_open = ssProto.connection_open()

        return render_template('config.html', port = port, form=uform, dform = dform,
            cform = cform, conn_open = conn_open, arduino_form = aform,
            gform = gform, iform = iform, diff_form = diff_form, wform = wform)

@app.route('/gain', methods=['POST'])
def gain():
    '''
    Configure the new gain for the arduino.
    '''
    gform = UpdateGainForm()
    global ssProto

    if gform.validate_on_submit():
        n_gain =  gform.gain.data;
        if ssProto.is_open():
            o_str = 'p{}'.format(n_gain)
            b = o_str.encode()
            ssProto.serial.write(b)
            flash('We set the gain to {}'.format(n_gain))
        else:
            flash('Serial port not open.', 'error')
        return redirect(url_for('config'))
    else:
        port = app.config['SERIAL_PORT']
        uform = UpdateForm()
        wform = SerialWaitForm()
        dform = DisconnectForm()
        cform = ConnectForm()

        aform = UpdateArduinoForm()
        iform = UpdateIntegralForm()
        diff_form = UpdateDifferentialForm()

        conn_open = ssProto.connection_open()

        return render_template('config.html', port = port, form=uform, dform = dform,
            cform = cform, conn_open = conn_open, arduino_form = aform,
            gform = gform, iform = iform, diff_form = diff_form, wform = wform)

@app.route('/integral', methods=['POST'])
def integral():
    '''
    Configure the new gain for the arduino.
    '''
    iform = UpdateIntegralForm()
    global ssProto

    if iform.validate_on_submit():
        n_tau =  iform.tau.data;
        if ssProto.is_open():
            o_str = 'i{}'.format(n_tau)
            b = o_str.encode()
            ssProto.serial.write(b)
            flash('We set the integration time  to {} seconds'.format(n_tau))
        else:
            flash('Serial port not open.', 'error')
        return redirect(url_for('config'))
    else:
        port = app.config['SERIAL_PORT']
        uform = UpdateForm()
        wform = SerialWaitForm()
        dform = DisconnectForm()
        cform = ConnectForm()

        aform = UpdateArduinoForm()
        gform = UpdateGainForm()
        diff_form = UpdateDifferentialForm()
        conn_open = ssProto.connection_open()

        return render_template('config.html', port = port, form=uform, dform = dform,
            cform = cform, conn_open = conn_open, arduino_form = aform,
            gform = gform, iform = iform, diff_form = diff_form, wform = wform)

@app.route('/diff', methods=['POST'])
def diff():
    '''
    Configure the new gain for the arduino.
    '''
    diff_form = UpdateDifferentialForm()
    global ssProto

    if diff_form.validate_on_submit():
        n_tau =  diff_form.tau.data;
        if ssProto.is_open():
            o_str = 'd{}'.format(n_tau)
            b = o_str.encode()
            ssProto.serial.write(b)
            flash('We set the differentiation time  to {} seconds'.format(n_tau))
        else:
            flash('Serial port not open.', 'error')
        return redirect(url_for('config'))
    else:
        port = app.config['SERIAL_PORT']
        uform = UpdateForm()
        wform = SerialWaitForm()
        dform = DisconnectForm()
        cform = ConnectForm()

        aform = UpdateArduinoForm()
        gform = UpdateGainForm()
        iform = UpdateIntegralForm()
        conn_open = ssProto.connection_open()

        return render_template('config.html', port = port, form=uform, dform = dform,
            cform = cform, conn_open = conn_open, arduino_form = aform,
            gform = gform, iform = iform, diff_form = diff_form, wform = wform)

@app.route('/file/<filename>')
def file(filename):
    '''function to save the values of the hdf5 file'''

    # We should add the latest value of the database here. Better would be to trigger the readout.
    # Let us see how this actually works.
    vals = ard_str.split(',');
    if vals:
        print(vals)
        with h5py.File(filename, "a") as f:
            if 'globals' in f.keys():
                params = f['globals']
                params.attrs['T_Verr'] = np.float(vals[0])
                params.attrs['T_Vmeas'] = np.float(vals[1])
                params.attrs['T_Vinp'] = np.float(vals[2])
                flash('Added the vals {} to the file {}'.format(ard_str, filename))
            else:
                flash('The file {} did not have the global group yet.'.format(filename), 'error')
    else:
        flash('Did not have any values to save', 'error')

    return render_template('file.html', file = filename, vals = vals)

# communication with the websocket
def get_arduino_data():
    '''
    A function to create test data for plotting.
    '''
    global ssProto;
    global ard_str;
    ser = ssProto.serial;
    # only read out on ask
    o_str = 'w'
    b = o_str.encode()
    ssProto.serial.write(b);
    stream = ser.read(ser.in_waiting);
    ard_str = stream.decode(encoding='windows-1252');
    timestamp = datetime.now().replace(microsecond=0).isoformat();
    return timestamp, ard_str

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

@socketio.on('my_ping')
def ping_pong():
    emit('my_pong')

# error handling
@app.errorhandler(500)
def internal_error(error):
    flash('An error occured {}'.format(error), 'error')
    return render_template('500.html'), 500
