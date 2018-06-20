from app import app, socketio
from app.forms import UpdateForm, DisconnectForm, ConnectForm, SerialWaitForm, ReConnectForm, SerialWaitForm
from app.forms import UpdateSetpointForm, UpdateGainForm, UpdateIntegralForm, UpdateDifferentialForm
from app.models import SerialArduinoTempControl
import h5py
import git
import numpy as np
from flask import render_template, flash, redirect, url_for, session

import time

from flask_socketio import emit, disconnect

# for subplots
import numpy as np

arduinos = [];

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
    name = arduino.name;
    port = arduino.serial.port;
    conn_open = arduino.connection_open()

    n_ards = len(arduinos);
    props = [];
    for ii, arduino in enumerate(arduinos):
        # create also the name for the readout field of the temperature
        temp_field_str = 'read' + str(arduino.id);
        dict = {'name': arduino.name, 'id': arduino.id, 'port': arduino.serial.port,
        'active': arduino.connection_open(), 'setpoint': arduino.setpoint,
        'label': temp_field_str};
        props.append(dict)

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
        ssProto = SerialArduinoTempControl(socketio, name);
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
            'gain': arduino.gain, 'tauI': arduino.integral, 'tauD': arduino.diff,
            'wait': arduino.sleeptime};

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
            'gain': arduino.gain, 'tauI': arduino.integral, 'tauD': arduino.diff,
            'wait': arduino.sleeptime};

        return render_template('change_arduino.html', form=uform, dform = dform,
            cform = cform,  sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, props=props);

@app.route('/serialwait', methods=['POST'])
def serialwait():
    '''
    Update the serial waiting time.
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

    id = int(wform.id.data);
    arduino = arduinos[id];

    if wform.validate_on_submit():

        arduino = arduinos[int(id)];
        n_wait =  wform.serial_time.data;
        try:
            arduino.sleeptime = n_wait;
            flash('We updated every {} s'.format(n_wait))
        except Exception as e:
             flash('{}'.format(e), 'error')
        return redirect(url_for('change_arduino', ard_nr = id))
    else:
        props = {'name': arduino.name, 'id': int(ard_nr), 'port': arduino.serial.port,
            'active': arduino.connection_open(), 'setpoint': arduino.setpoint,
            'gain': arduino.gain, 'tauI': arduino.integral, 'tauD': arduino.diff,
            'wait': arduino.sleeptime};

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
                'gain': arduino.gain, 'tauI': arduino.integral, 'tauD': arduino.diff,
                'wait': arduino.sleeptime};

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
                'gain': arduino.gain, 'tauI': arduino.integral, 'tauD': arduino.diff,
                'wait': arduino.sleeptime};
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
                'gain': arduino.gain, 'tauI': arduino.integral, 'tauD': arduino.diff,
                'wait': arduino.sleeptime};

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
                'gain': arduino.gain, 'tauI': arduino.integral, 'tauD': arduino.diff,
                'wait': arduino.sleeptime};

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

@app.route('/file/<filestring>')
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

    global arduinos;

    if id >= len(arduinos):
        flash('Arduino Index out of range.')
        return redirect(url_for('index'))

    arduino = arduinos[id];
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
