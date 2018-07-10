from app import app, socketio, db

from app.serialmonitor import bp
from app.serialmonitor.forms import ConnectForm, UpdateForm, SerialWaitForm, DisconnectForm
from app.serialmonitor.models import serialmonitors, ArduinoSerial

from flask import render_template, flash, redirect, url_for, session

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
    sopen = sm.start();
    flash('Trying to start the serial monitor')
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
        try:
            if arduino.connection_open():
                arduino.stop();
            arduino.update_serial(n_port);
            if arduino.is_open():
                flash('We updated the serial to {}'.format(n_port))
            else:
                flash('Update of the serial port went wrong.', 'error')
        except Exception as e:
             flash('{}'.format(e), 'error')
        return redirect(url_for('serialmonitor.change_serialmonitor', ard_nr = id))
    else:
        props = {'name': arduino.name, 'id': arduino.id, 'port': arduino.serial_port,
            'active': arduino.connection_open(), 'wait': arduino.sleeptime};

        return render_template('change_serialmonitor.html',
            form=uform, dform = dform, wform = wform, props=props);
