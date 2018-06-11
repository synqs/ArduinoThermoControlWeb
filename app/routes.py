from app import app, socketio
from app.forms import UpdateForm, DisconnectForm, ConnectForm, SerialWaitForm, ReConnectForm
from app.forms import UpdateSetpointForm, UpdateGainForm, UpdateIntegralForm, UpdateDifferentialForm
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

arduinos = [];
ard_str = '';

class SerialSocketProtocol(object):
    '''
    A class which combines the serial connection and the socket into a single
    class, such that we can handle these things more properly.
    '''

    serial = None
    switch = False
    unit_of_work = 0
    name = '';
    id = 0;
    setpoint = '';
    diff = None;
    integral = None;
    gain = None;

    def __init__(self, socketio):
        """
        assign socketio object to emit
        """
        self.serial = serial.Serial()
        self.switch = False
        self.socketio = socketio

    def __init__(self, socketio, name):
        """
        assign socketio object to emit
        """
        self.serial = serial.Serial()
        self.switch = False
        self.socketio = socketio
        self.name = name;

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
        if self.is_open():
            self.serial.close()

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
                    timestamp, ard_str = self.pull_data()

                    vals = ard_str.split(',');
                    if len(vals)>=2:
                        self.socketio.emit('temp_value',
                            {'data': vals[1], 'id': self.id})

                    self.socketio.emit('log_response',
                    {'time':timestamp, 'data': vals, 'count': self.unit_of_work,
                        'id': self.id})
                except Exception as e:
                    print('{}'.format(e))
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

    def pull_data(self):
        '''
        Pulling the actual data from the arduino.
        '''
        global ard_str;
        ser = self.serial;
        # only read out on ask
        o_str = 'w'
        b = o_str.encode()
        ser.write(b);
        stream = ser.read(ser.in_waiting);
        ard_str = stream.decode(encoding='windows-1252');
        timestamp = datetime.now().replace(microsecond=0).isoformat();
        return timestamp, ard_str

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

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    '''
    The main function for rendering the principal site.
    '''
    global arduinos

    n_ards = len(arduinos);
    props = [];
    for ii, arduino in enumerate(arduinos):
        # create also the name for the readout field of the temperature
        temp_field_str = 'read' + str(arduino.id);
        dict = {'name': arduino.name, 'id': arduino.id, 'port': arduino.serial.port,
        'active': arduino.connection_open(), 'setpoint': arduino.setpoint,
        'label': temp_field_str};
        props.append(dict)

    return render_template('index.html',n_ards = n_ards, props = props);


@app.route('/details/<ard_nr>', methods=['GET', 'POST'])
def details(ard_nr):
    '''
    The main function for rendering the principal site.
    '''
    global arduinos;
    if not arduinos:
        flash('No arduinos installed', 'error')
        return redirect(url_for('index'))

    n_ards = len(arduinos);

    arduino = arduinos[int(ard_nr)];
    n_ards = len(arduinos);
    props = [];
    for ii, arduino in enumerate(arduinos):
        # create also the name for the readout field of the temperature
        temp_field_str = 'read' + str(arduino.id);
        dict = {'name': arduino.name, 'id': arduino.id, 'port': arduino.serial.port,
        'active': arduino.connection_open(), 'setpoint': arduino.setpoint,
        'label': temp_field_str};
        props.append(dict)

    name = arduino.name;
    port = arduino.serial.port;
    conn_open = arduino.connection_open()
    return render_template('details.html',n_ards = n_ards, props = props, ard_nr = ard_nr,
        name = name, conn_open = conn_open);

@app.route('/overview')
def overview():
    '''
    The  function summarizing the status of each Arduino.
    '''
    global arduinos
    n_ards = len(arduinos);
    props = [];
    for arduino in arduinos:
        dict = {'name': arduino.name, 'port': arduino.serial.port};
        props.append(dict)
    return render_template('status_overview.html', n_ards = n_ards, props = props)

@app.route('/add_arduino', methods=['GET', 'POST'])
def add_arduino():
    '''
    Add an arduino to the set up
    '''
    global arduinos;
    cform = ConnectForm();

    if cform.validate_on_submit():
        n_port =  cform.serial_port.data;
        name = cform.name.data;
        ssProto = SerialSocketProtocol(socketio, name);
        ssProto.id = len(arduinos)
        try:
            ssProto.open_serial(n_port, 9600, timeout = 1)
            ssProto.start()
            if ssProto.is_open():
                app.config['SERIAL_PORT'] = n_port;
                arduinos.append(ssProto)
                flash('We added a new arduino {}'.format(app.config['SERIAL_PORT']))
                return redirect(url_for('index'))
            else:
                 flash('Adding the Arduino went wrong', 'error')
                 return redirect(url_for('add_arduino'))
        except Exception as e:
             flash('{}'.format(e), 'error')
             return redirect(url_for('add_arduino'))

    port = app.config['SERIAL_PORT']
    n_ards = len(arduinos)
    return render_template('add_arduino.html', port = port, cform = cform, n_ards=n_ards);

def change_arduino_param(ard_nr):
    '''
    The function, which allows to combine the different views
    '''

@app.route('/change_arduino/<ard_nr>')
def change_arduino(ard_nr):
    '''
    Change the parameters of a specific arduino
    '''
    global arduinos;
    if not arduinos:
        flash('No arduinos installed', 'error')
        return redirect(url_for('add_arduino'))

    n_ards = len(arduinos);
    arduino = arduinos[int(ard_nr)];
    props = {'name': arduino.name, 'id': int(ard_nr), 'port': arduino.serial.port,
            'active': arduino.connection_open(), 'setpoint': arduino.setpoint,
            'gain': arduino.gain, 'tauI': arduino.integral, 'tauD': arduino.diff};

    uform = UpdateForm(id=ard_nr)

    sform = UpdateSetpointForm(id=ard_nr)
    gform = UpdateGainForm(id=ard_nr)
    iform = UpdateIntegralForm(id=ard_nr)
    diff_form = UpdateDifferentialForm(id=ard_nr)

    wform = SerialWaitForm(id=ard_nr)
    dform = DisconnectForm(id=ard_nr)
    cform = ReConnectForm(id=ard_nr)

    return render_template('change_arduino.html',
        form=uform, dform = dform, cform = cform,  sform = sform,
        gform = gform, iform = iform,diff_form = diff_form, wform = wform, props=props);

@app.route('/update', methods=['POST'])
def update():
    '''
    Update the serial port.
    '''
    global arduinos
    if not arduinos:
        flash('No arduino yet.', 'error')
        return redirect(url_for('add_arduino'))

    sform = UpdateSetpointForm();
    uform = UpdateForm();
    wform = SerialWaitForm()
    dform = DisconnectForm()
    cform = ReConnectForm()
    gform = UpdateGainForm()
    iform = UpdateIntegralForm()
    diff_form = UpdateDifferentialForm()

    id = int(uform.id.data);
    arduino = arduinos[id];

    if uform.validate_on_submit():

        arduino = arduinos[int(id)];
        n_port =  uform.serial_port.data;
        try:
            if arduino.connection_open():
                arduino.stop()
            arduino.open_serial(n_port, 9600, timeout = 1)
            arduino.start()
            if arduino.is_open():
                flash('We updated the serial to {}'.format(n_port))
            else:
                flash('Update of the serial port went wrong.', 'error')
        except Exception as e:
             flash('{}'.format(e), 'error')
        return redirect(url_for('change_arduino', ard_nr = id))
    else:
        props = {'name': arduino.name, 'id': int(ard_nr), 'port': arduino.serial.port,
            'active': arduino.connection_open(), 'setpoint': arduino.setpoint,
            'gain': arduino.gain, 'tauI': arduino.integral, 'tauD': arduino.diff};

        return render_template('change_arduino.html', form=uform, dform = dform,
            cform = cform,  sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, props=props);

@app.route('/setpoint', methods=['POST'])
def arduino():
    '''
    Configure now settings for the arduino.
    '''
    global arduinos
    if not arduinos:
        flash('No arduino yet.', 'error')
        return redirect(url_for('add_arduino'))

    sform = UpdateSetpointForm();
    uform = UpdateForm();
    wform = SerialWaitForm()
    dform = DisconnectForm()
    cform = ReConnectForm()
    gform = UpdateGainForm()
    iform = UpdateIntegralForm()
    diff_form = UpdateDifferentialForm()

    id = int(sform.id.data);
    arduino = arduinos[id];

    if sform.validate_on_submit():
        n_setpoint =  sform.setpoint.data;
        if arduino.is_open():
            o_str = 's{}'.format(n_setpoint)
            b = o_str.encode()
            arduino.serial.write(b)
            arduino.setpoint = n_setpoint;
            flash('We set the setpoint to {}'.format(n_setpoint))
        else:
            flash('Serial port not open.', 'error')
        return redirect(url_for('change_arduino', ard_nr = id))
    else:
        props = {'name': arduino.name, 'id': int(ard_nr), 'port': arduino.serial.port,
                'active': arduino.connection_open(), 'setpoint': arduino.setpoint,
                'gain': arduino.gain, 'tauI': arduino.integral, 'tauD': arduino.diff};

        return render_template('change_arduino.html', form=uform, dform = dform,
            cform = cform,  sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, props=props);

@app.route('/gain', methods=['POST'])
def gain():
    '''
    Configure the new gain for the arduino.
    '''
    global arduinos
    if not arduinos:
        flash('No arduino yet.', 'error')
        return redirect(url_for('add_arduino'))

    sform = UpdateSetpointForm();
    uform = UpdateForm();
    wform = SerialWaitForm()
    dform = DisconnectForm()
    cform = ReConnectForm()
    gform = UpdateGainForm()
    iform = UpdateIntegralForm()
    diff_form = UpdateDifferentialForm()

    id = int(gform.id.data);
    arduino = arduinos[id];

    if gform.validate_on_submit():
        n_gain =  gform.gain.data;
        if arduino.is_open():
            o_str = 'p{}'.format(n_gain)
            b = o_str.encode()
            arduino.serial.write(b)
            arduino.gain =  n_gain;
            flash('We set the gain to {}'.format(n_gain))
        else:
            flash('Serial port not open.', 'error')
        return redirect(url_for('change_arduino', ard_nr = id))
    else:
        props = {'name': arduino.name, 'id': id, 'port': arduino.serial.port,
                'active': arduino.connection_open(), 'setpoint': arduino.setpoint,
                'gain': arduino.gain, 'tauI': arduino.integral, 'tauD': arduino.diff};
        return render_template('change_arduino.html', form=uform, dform = dform,
            cform = cform,  sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, props=props);

@app.route('/integral', methods=['POST'])
def integral():
    '''
    Configure the new gain for the arduino.
    '''
    global arduinos
    if not arduinos:
        flash('No arduino yet.', 'error')
        return redirect(url_for('add_arduino'))

    sform = UpdateSetpointForm();
    uform = UpdateForm();
    wform = SerialWaitForm()
    dform = DisconnectForm()
    cform = ReConnectForm()
    gform = UpdateGainForm()
    iform = UpdateIntegralForm()
    diff_form = UpdateDifferentialForm()

    id = int(iform.id.data);
    arduino = arduinos[id];

    if iform.validate_on_submit():
        n_tau =  iform.tau.data;
        if arduino.is_open():
            o_str = 'i{}'.format(n_tau)
            b = o_str.encode()
            arduino.serial.write(b)
            arduino.integral =  n_tau;
            flash('We set the integration time  to {} seconds'.format(n_tau))
        else:
            flash('Serial port not open.', 'error')
        return redirect(url_for('change_arduino', ard_nr = id))
    else:
        props = {'name': arduino.name, 'id': id, 'port': arduino.serial.port,
                'active': arduino.connection_open(), 'setpoint': arduino.setpoint,
                'gain': arduino.gain, 'tauI': arduino.integral, 'tauD': arduino.diff};

        return render_template('change_arduino.html', form=uform, dform = dform,
            cform = cform,  sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, props=props);

@app.route('/diff', methods=['POST'])
def diff():
    '''
    Configure the new gain for the arduino.
    '''
    global arduinos
    if not arduinos:
        flash('No arduino yet.', 'error')
        return redirect(url_for('add_arduino'))

    sform = UpdateSetpointForm();
    uform = UpdateForm();
    wform = SerialWaitForm()
    dform = DisconnectForm()
    cform = ReConnectForm()
    gform = UpdateGainForm()
    iform = UpdateIntegralForm()
    diff_form = UpdateDifferentialForm()

    id = int(diff_form.id.data);
    arduino = arduinos[id];

    if diff_form.validate_on_submit():
        n_tau =  diff_form.tau.data;
        if arduino.is_open():
            o_str = 'd{}'.format(n_tau)
            b = o_str.encode()
            arduino.serial.write(b)
            arduino.diff =  n_tau;
            flash('We set the differentiation time  to {} seconds'.format(n_tau))
        else:
            flash('Serial port not open.', 'error')
        return redirect(url_for('change_arduino', ard_nr = id))
    else:
        props = {'name': arduino.name, 'id': id, 'port': arduino.serial.port,
                'active': arduino.connection_open(), 'setpoint': arduino.setpoint,
                'gain': arduino.gain, 'tauI': arduino.integral, 'tauD': arduino.diff};

        return render_template('change_arduino.html', form=uform, dform = dform,
            cform = cform,  sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, props=props);

@app.route('/start', methods=['POST'])
def start():

    cform = ReConnectForm()

    global arduinos;
    if arduinos:
        ssProto = arduinos[0];
    else:
        flash('No arduino connection existing yet', 'error')
        return redirect(url_for('add_arduino'))

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
    global arduinos;
    if arduinos:
        ssProto = arduinos[0];
    else:
        flash('Nothing to disconnect from', 'error')

    if dform.validate_on_submit():
        #Disconnect the port.
        ssProto.stop()
        ssProto.serial.close()

        flash('Closed the serial connection')
        return redirect(url_for('config'))

    return redirect(url_for('config'))

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

    global arduinos;
    # we should even kill the arduino properly.
    if arduinos:
        ssProto = arduinos[0];
        ser = ssProto.serial;
        ser.close();
        ssProto.stop();
        emit('my_response',
            {'data': 'Disconnected!', 'count': session['receive_count']})
    else:
        emit('my_response',
            {'data': 'Nothing to disconnect', 'count': session['receive_count']})

@socketio.on('my_ping')
def ping_pong():
    emit('my_pong')

# error handling
@app.errorhandler(500)
def internal_error(error):
    flash('An error occured {}'.format(error), 'error')
    return render_template('500.html'), 500
