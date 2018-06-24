from app.thermocontrol import bp
from app.thermocontrol.forms import ConnectForm, UpdateForm, SerialWaitForm, DisconnectForm
from app.thermocontrol.forms import UpdateSetpointForm, UpdateGainForm, UpdateIntegralForm, UpdateDifferentialForm
from app.thermocontrol.models import SerialArduinoTempControl, tempcontrols
from app import app, socketio

from flask import render_template, flash, redirect, url_for, session


@bp.route('/details/<ard_nr>', methods=['GET', 'POST'])
def details(ard_nr):
    '''
    The main function for rendering the principal site.
    '''
    global tempcontrols;
    if not tempcontrols:
        flash('No tempcontrols installed', 'error')
        return redirect(url_for('main.index'))

    n_ards = len(tempcontrols);

    arduino = tempcontrols[int(ard_nr)];
    name = arduino.name;
    port = arduino.serial.port;
    conn_open = arduino.connection_open()

    n_ards = len(tempcontrols);
    props = [];
    for ii, arduino in enumerate(tempcontrols):
        # create also the name for the readout field of the temperature
        temp_field_str = 'read' + str(arduino.id);
        dict = {'name': arduino.name, 'id': arduino.id, 'port': arduino.serial.port,
        'active': arduino.connection_open(), 'setpoint': arduino.setpoint,
        'label': temp_field_str};
        props.append(dict)

    return render_template('details.html',n_ards = n_ards, props = props, ard_nr = ard_nr,
        name = name, conn_open = conn_open);

@bp.route('/add_tempcontrol', methods=['GET', 'POST'])
def add_tempcontrol():
    '''
    Add an arduino to the set up
    '''
    global tempcontrols;
    cform = ConnectForm();

    if cform.validate_on_submit():
        n_port =  cform.serial_port.data;
        name = cform.name.data;
        ssProto = SerialArduinoTempControl(socketio, name);
        ssProto.id = len(tempcontrols)
        try:
            ssProto.open_serial(n_port, 9600, timeout = 1)
            ssProto.start()
            if ssProto.is_open():
                app.config['SERIAL_PORT'] = n_port;
                tempcontrols.append(ssProto)
                flash('We added a new arduino {}'.format(app.config['SERIAL_PORT']))
                return redirect(url_for('main.index'))
            else:
                 flash('Adding the Arduino went wrong', 'error')
                 return redirect(url_for('thermocontrol.add_tempcontrol'))
        except Exception as e:
             flash('{}'.format(e), 'error')
             return redirect(url_for('thermocontrol.add_tempcontrol'))

    port = app.config['SERIAL_PORT']
    n_ards = len(tempcontrols)
    return render_template('add_arduino.html', port = port, cform = cform, n_ards=n_ards,
    device_type = 'temp control');

@bp.route('/change_arduino/<ard_nr>')
def change_arduino(ard_nr):
    '''
    Change the parameters of a specific arduino
    '''
    global tempcontrols;
    if not tempcontrols:
        flash('No tempcontrols installed', 'error')
        return redirect(url_for('thermocontrol.add_tempcontrol'))

    n_ards = len(tempcontrols);
    arduino = tempcontrols[int(ard_nr)];
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

    return render_template('change_arduino.html',
        form=uform, dform = dform, sform = sform,
        gform = gform, iform = iform,diff_form = diff_form, wform = wform, props=props);

@bp.route('/update', methods=['POST'])
def update():
    '''
    Update the serial port.
    '''
    global tempcontrols
    if not tempcontrols:
        flash('No arduino yet.', 'error')
        return redirect(url_for('add_tempcontrol'))

    sform = UpdateSetpointForm();
    uform = UpdateForm();
    wform = SerialWaitForm()
    dform = DisconnectForm()
    gform = UpdateGainForm()
    iform = UpdateIntegralForm()
    diff_form = UpdateDifferentialForm()

    id = int(uform.id.data);
    arduino = tempcontrols[id];

    if uform.validate_on_submit():

        arduino = tempcontrols[int(id)];
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
        return redirect(url_for('thermocontrol.change_arduino', ard_nr = id))
    else:
        props = {'name': arduino.name, 'id': int(ard_nr), 'port': arduino.serial.port,
            'active': arduino.connection_open(), 'setpoint': arduino.setpoint,
            'gain': arduino.gain, 'tauI': arduino.integral, 'tauD': arduino.diff,
            'wait': arduino.sleeptime};

        return render_template('change_arduino.html', form=uform, dform = dform,
            cform = cform,  sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, props=props);

@bp.route('/serialwait', methods=['POST'])
def serialwait():
    '''
    Update the serial waiting time.
    '''
    global tempcontrols
    if not tempcontrols:
        flash('No arduino yet.', 'error')
        return redirect(url_for('add_tempcontrol'))

    sform = UpdateSetpointForm();
    uform = UpdateForm();
    wform = SerialWaitForm()
    dform = DisconnectForm()
    gform = UpdateGainForm()
    iform = UpdateIntegralForm()
    diff_form = UpdateDifferentialForm()

    id = int(wform.id.data);
    arduino = tempcontrols[id];

    if wform.validate_on_submit():

        arduino = tempcontrols[int(id)];
        n_wait =  wform.serial_time.data;
        try:
            arduino.sleeptime = n_wait;
            flash('We updated every {} s'.format(n_wait))
        except Exception as e:
             flash('{}'.format(e), 'error')
        return redirect(url_for('thermocontrol.change_arduino', ard_nr = id))
    else:
        props = {'name': arduino.name, 'id': int(ard_nr), 'port': arduino.serial.port,
            'active': arduino.connection_open(), 'setpoint': arduino.setpoint,
            'gain': arduino.gain, 'tauI': arduino.integral, 'tauD': arduino.diff,
            'wait': arduino.sleeptime};

        return render_template('change_arduino.html', form=uform, dform = dform,
            cform = cform,  sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, props=props);

@bp.route('/setpoint', methods=['POST'])
def arduino():
    '''
    Configure now settings for the arduino.
    '''
    global tempcontrols
    if not tempcontrols:
        flash('No arduino yet.', 'error')
        return redirect(url_for('add_tempcontrol'))

    sform = UpdateSetpointForm();
    uform = UpdateForm();
    wform = SerialWaitForm()
    dform = DisconnectForm()
    gform = UpdateGainForm()
    iform = UpdateIntegralForm()
    diff_form = UpdateDifferentialForm()

    id = int(sform.id.data);
    arduino = tempcontrols[id];

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
        return redirect(url_for('thermocontrol.change_arduino', ard_nr = id))
    else:
        props = {'name': arduino.name, 'id': int(ard_nr), 'port': arduino.serial.port,
                'active': arduino.connection_open(), 'setpoint': arduino.setpoint,
                'gain': arduino.gain, 'tauI': arduino.integral, 'tauD': arduino.diff,
                'wait': arduino.sleeptime};

        return render_template('change_arduino.html', form=uform, dform = dform,
            cform = cform,  sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, props=props);

@bp.route('/gain', methods=['POST'])
def gain():
    '''
    Configure the new gain for the arduino.
    '''
    global tempcontrols
    if not tempcontrols:
        flash('No arduino yet.', 'error')
        return redirect(url_for('add_tempcontrol'))

    sform = UpdateSetpointForm();
    uform = UpdateForm();
    wform = SerialWaitForm()
    dform = DisconnectForm()
    gform = UpdateGainForm()
    iform = UpdateIntegralForm()
    diff_form = UpdateDifferentialForm()

    id = int(gform.id.data);
    arduino = tempcontrols[id];

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
        return redirect(url_for('thermocontrol.change_arduino', ard_nr = id))
    else:
        props = {'name': arduino.name, 'id': id, 'port': arduino.serial.port,
                'active': arduino.connection_open(), 'setpoint': arduino.setpoint,
                'gain': arduino.gain, 'tauI': arduino.integral, 'tauD': arduino.diff,
                'wait': arduino.sleeptime};
        return render_template('change_arduino.html', form=uform, dform = dform,
            cform = cform,  sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, props=props);

@bp.route('/integral', methods=['POST'])
def integral():
    '''
    Configure the new gain for the arduino.
    '''
    global tempcontrols
    if not tempcontrols:
        flash('No arduino yet.', 'error')
        return redirect(url_for('add_tempcontrol'))

    sform = UpdateSetpointForm();
    uform = UpdateForm();
    wform = SerialWaitForm()
    dform = DisconnectForm()
    gform = UpdateGainForm()
    iform = UpdateIntegralForm()
    diff_form = UpdateDifferentialForm()

    id = int(iform.id.data);
    arduino = tempcontrols[id];

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
        return redirect(url_for('thermocontrol.change_arduino', ard_nr = id))
    else:
        props = {'name': arduino.name, 'id': id, 'port': arduino.serial.port,
                'active': arduino.connection_open(), 'setpoint': arduino.setpoint,
                'gain': arduino.gain, 'tauI': arduino.integral, 'tauD': arduino.diff,
                'wait': arduino.sleeptime};

        return render_template('change_arduino.html', form=uform, dform = dform,
            cform = cform,  sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, props=props);

@bp.route('/diff', methods=['POST'])
def diff():
    '''
    Configure the new gain for the arduino.
    '''
    global tempcontrols
    if not tempcontrols:
        flash('No arduino yet.', 'error')
        return redirect(url_for('add_tempcontrol'))

    sform = UpdateSetpointForm();
    uform = UpdateForm();
    wform = SerialWaitForm()
    dform = DisconnectForm()
    gform = UpdateGainForm()
    iform = UpdateIntegralForm()
    diff_form = UpdateDifferentialForm()

    id = int(diff_form.id.data);
    arduino = tempcontrols[id];

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
        return redirect(url_for('thermocontrol.change_arduino', ard_nr = id))
    else:
        props = {'name': arduino.name, 'id': id, 'port': arduino.serial.port,
                'active': arduino.connection_open(), 'setpoint': arduino.setpoint,
                'gain': arduino.gain, 'tauI': arduino.integral, 'tauD': arduino.diff,
                'wait': arduino.sleeptime};

        return render_template('change_arduino.html', form=uform, dform = dform,
            sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, props=props);

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

    global tempcontrols;
    # we should even kill the arduino properly.
    if tempcontrols:
        ssProto = tempcontrols[0];
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
