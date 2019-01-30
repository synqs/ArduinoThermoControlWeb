from app import app, socketio, db

from app.serialmonitor import bp
from app.serialmonitor.forms import ConnectForm, UpdateForm, SerialWaitForm, DisconnectForm
from app.serialmonitor.models import ArduinoSerial

from flask import render_template, flash, redirect, url_for, session

from serial.serialutil import SerialException

import h5py

@bp.route('/details_serialmonitor/<int:ard_nr>', methods=['GET', 'POST'])
def details_serialmonitor(ard_nr):
    '''
    The main function for rendering the principal site.
    '''
    arduino = ArduinoSerial.query.get(ard_nr);
    name = arduino.name;
    port = arduino.serial_port;
    conn_open = arduino.connection_open()

    tempcontrols = ArduinoSerial.query.all();
    n_ards = len(tempcontrols);

    return render_template('details_serialmonitor.html', ard = arduino, ard_nr = ard_nr,
        name = name, conn_open = conn_open);

@bp.route('/add_serialmonitor', methods=['GET', 'POST'])
def add_serialmonitor():
    '''
    Add an arduino to the set up
    '''
    cform = ConnectForm();

    if cform.validate_on_submit():
        n_port =  cform.serial_port.data;
        name = cform.name.data;
        sm = ArduinoSerial(name=name, serial_port = n_port, sleeptime=3);
        db.session.add(sm);
        db.session.commit();
        flash('We added a new arduino {}'.format(name))
        return redirect(url_for('main.index'))

    port = app.config['SERIAL_PORT'];
    serialmonitors = ArduinoSerial.query.all();
    n_ards = len(serialmonitors)
    return render_template('add_arduino.html', port = port, cform = cform, n_ards=n_ards,
    device_type = 'serial monitor');

@bp.route('/remove_serialmonitor/<int:ard_nr>')
def remove_serialmonitor(ard_nr):
    tc = ArduinoSerial.query.get(ard_nr);
    db.session.delete(tc)
    db.session.commit()

    flash('Removed the serial monitor # {}.'.format(ard_nr));
    return redirect(url_for('main.index'))

@bp.route('/start_serialmonitor/<int:ard_nr>')
def start_serialmonitor(ard_nr):
    '''
    The main function for rendering the principal site.
    '''
    sm = ArduinoSerial.query.get(ard_nr);
    try:
        sopen = sm.start();
        flash('Trying to start the serial monitor');
    except SerialException as e:
        flash('SerialException: Could not open serial connection', 'error')

    return redirect(url_for('main.index'))

@bp.route('/stop_serialmonitor/<int:ard_nr>')
def stop_serialmonitor(ard_nr):
    '''
    The main function for rendering the principal site.
    '''
    tc = ArduinoSerial.query.get(ard_nr);
    tc.stop()
    flash('Stopped the serial monitor')
    return redirect(url_for('main.index'))

@bp.route('/change_serialmonitor/<ard_nr>')
def change_serialmonitor(ard_nr):
    '''
    Change the parameters of a specific arduino
    '''

    arduino = ArduinoSerial.query.get(ard_nr);
    if not arduino:
        flash('No serialmonitors installed', 'error')
        return redirect(url_for('serialmonitor.add_serialmonitor'))

    uform = UpdateForm(id=ard_nr)
    wform = SerialWaitForm(id=ard_nr)
    dform = DisconnectForm(id=ard_nr)

    return render_template('change_serialmonitor.html',
        form=uform, dform = dform, wform = wform, ard=arduino);

@bp.route('/update_sm', methods=['POST'])
def update_sm():
    '''
    Update the serial port.
    '''

    uform = UpdateForm();
    wform = SerialWaitForm()
    dform = DisconnectForm()

    id = int(uform.id.data);
    arduino = ArduinoSerial.query.get(id);

    if uform.validate_on_submit():
        n_port =  uform.serial_port.data;
        n_br =  uform.baud_rate.data;
        try:
            if arduino.connection_open():
                arduino.stop();
            arduino.update_serial(n_port, n_br);
            if arduino.is_open():
                flash('We updated the serial to {}'.format(n_port))
            else:
                flash('Update of the serial port went wrong.', 'error')
        except Exception as e:
             flash('{}'.format(e), 'error')
        return redirect(url_for('serialmonitor.change_serialmonitor', ard_nr = id))
    else:
        return render_template('change_serialmonitor.html',
            form=uform, dform = dform, wform = wform, ard = arduino);

@bp.route('/wait_sm', methods=['POST'])
def wait_sm():
    '''
    Update the serial waiting time.
    '''
    uform = UpdateForm();
    wform = SerialWaitForm()
    dform = DisconnectForm()

    id = int(wform.id.data);
    arduino = ArduinoSerial.query.get(id);

    if wform.validate_on_submit():

        n_wait =  wform.serial_time.data;
        arduino.sleeptime = n_wait;
        db.session.commit();
        flash('We update every {} s'.format(n_wait))
        return redirect(url_for('serialmonitor.change_serialmonitor', ard_nr = id))
    else:
        return render_template('change_serialmonitor.html',
            form=uform, dform = dform, wform = wform, ard=arduino);

@bp.route('/save_sm/<filestring>')
def file(filestring):
    '''function to save the values of the hdf5 file. It should have the following structure
    <ard_nr>+<filename>
    '''
    # first let us devide into the right parts
    parts = filestring.split('+');
    if not len(parts) == 2:
        flash('The filestring should be of the form <ard_nr>+<filename>')
        return redirect(url_for('main.index'))

    filename = parts[1]
    id = int(parts[0])

    arduino = ArduinoSerial.query.get(id);

    if not arduino:
        flash('Aruduino not installed', 'error')
        return redirect(url_for('main.index'));

    vals = arduino.get_current_data();
    param_name = 'sm' + parts[0];
    with h5py.File(filename, "a") as f:
        if 'globals' in f.keys():
            params = f['globals']
            for el, val in enumerate(vals):
                param_name = 'sm' + parts[0] + '_' +str(el);
                print(param_name)
                params.attrs[param_name] = float(val)
                flash('Added the serial value {} to the file {}'.format(val, filename))
        else:
            flash('The file {} did not have the global group yet.'.format(filename), 'error')

    return render_template('file.html', file = filename)
