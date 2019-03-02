from app.thermocontrol import bp
from app.thermocontrol.forms import ConnectForm, UpdateForm, SerialWaitForm, DisconnectForm, WebConnectForm
from app.thermocontrol.forms import UpdateSetpointForm, UpdateGainForm, UpdateIntegralForm, UpdateDifferentialForm
from app.thermocontrol.models import TempControl, WebTempControl
from app.thermocontrol.utils import start_helper, get_wtc_forms, get_wtc_forms_wo_id
from app.thermocontrol.utils import get_tc_forms, get_tc_forms_wo_id

from app import socketio, db

from flask import render_template, flash, redirect, url_for, session

@bp.route('/details/<int:ard_nr>', methods=['GET', 'POST'])
def details(ard_nr):
    '''
    The main function for rendering the principal site.
    '''
    arduino = TempControl.query.get(ard_nr);
    device_type = 'serial_tc';

    if not arduino:
        flash('No tempcontrols installed', 'error')
        return redirect(url_for('thermocontrol.add_tempcontrol'));

    return render_template('details.html', ard=arduino, device_type=device_type);

@bp.route('/details_wtc/<int:ard_nr>', methods=['GET', 'POST'])
def details_wtc(ard_nr):
    '''
    The main function for rendering the principal site.
    '''
    arduino = WebTempControl.query.get(ard_nr);
    device_type = 'web_tc';

    if not arduino:
        flash('No tempcontrols installed', 'error')
        return redirect(url_for('thermocontrol.add_webtempcontrol'));

    return render_template('details.html', ard=arduino, device_type=device_type);

@bp.route('/add_tempcontrol', methods=['GET', 'POST'])
def add_tempcontrol():
    '''
    Add an arduino to the set up
    '''
    cform = ConnectForm();

    if cform.validate_on_submit():
        n_port =  cform.serial_port.data;
        name = cform.name.data;
        tc = TempControl(name=name, serial_port = n_port, sleeptime=3);
        db.session.add(tc);
        db.session.commit();
        flash('We added a new arduino {}'.format(name))
        return redirect(url_for('main.index'))

    port = app.config['SERIAL_PORT']
    tempcontrols = TempControl.query.all();
    n_ards = len(tempcontrols)
    return render_template('add_arduino.html', port = port, cform = cform, n_ards=n_ards,
    device_type = 'temp control');

@bp.route('/add_webtempcontrol', methods=['GET', 'POST'])
def add_webtempcontrol():
    '''
    Add an arduino with ethernet interface to the set up
    '''
    cform = WebConnectForm();

    if cform.validate_on_submit():
        ip_adress = cform.ip_adress.data;
        port = cform.port.data;
        name = cform.name.data;
        if not port:
            port = 80;
        tc = WebTempControl(name=name, ip_adress= ip_adress, port = port, sleeptime=3);

        db.session.add(tc);
        db.session.commit();
        flash('We added a new arduino {}'.format(name))
        return redirect(url_for('main.index'))

    tempcontrols = WebTempControl.query.all();
    n_ards = len(tempcontrols)
    return render_template('add_webarduino.html', cform = cform, n_ards=n_ards,
    device_type = 'web temp control');


@bp.route('/remove/<int:ard_nr>')
def remove(ard_nr):
    tc = TempControl.query.get(ard_nr);
    db.session.delete(tc)
    db.session.commit()

    flash('Removed the temperature control # {}.'.format(ard_nr));
    return redirect(url_for('main.index'))

@bp.route('/remove_wtc/<int:ard_nr>')
def remove_wtc(ard_nr):
    tc = WebTempControl.query.get(ard_nr);
    db.session.delete(tc)
    db.session.commit()

    flash('Removed the web temperature control # {}.'.format(ard_nr));
    return redirect(url_for('main.index'))

@bp.route('/start_tc/<int:ard_nr>')
def start_tc(ard_nr):
    '''
    The main function for rendering the principal site.
    '''
    tc = TempControl.query.get(ard_nr);
    return start_helper(tc);

@bp.route('/start_wtc/<int:ard_nr>')
def start_wtc(ard_nr):
    '''
    The main function for rendering the principal site.
    '''
    tc = WebTempControl.query.get(ard_nr);
    return start_helper(tc);

@bp.route('/stop/<int:ard_nr>')
def stop(ard_nr):
    '''
    The main function for rendering the principal site.
    '''
    tc = TempControl.query.get(ard_nr);
    tc.stop()
    flash('Stopped the thermocontrol')
    return redirect(url_for('main.index'))

@bp.route('/stop_wtc>/<int:ard_nr>')
def stop_wtc(ard_nr):
    '''
    The main function for rendering the principal site.
    '''
    tc = WebTempControl.query.get(ard_nr);
    tc.stop()
    flash('Stopped the thermocontrol')
    return redirect(url_for('main.index'))

@bp.route('/change_arduino/<int:ard_nr>')
def change_arduino(ard_nr):
    '''
    Change the parameters of a specific arduino
    '''
    arduino = TempControl.query.get(ard_nr);
    device_type = 'serial_tc';

    if not arduino:
        flash('No tempcontrols installed', 'error')
        return redirect(url_for('thermocontrol.add_tempcontrol'));

    uform, sform, gform, iform, diff_form, wform, dform = get_tc_forms(ard_nr);

    return render_template('change_arduino.html',
        form=uform, dform = dform, sform = sform, gform = gform, iform = iform,
        diff_form = diff_form, wform = wform, ard=arduino, device_type=device_type);

@bp.route('/change_wtc/<int:ard_nr>')
def change_wtc(ard_nr):
    '''
    Change the parameters of a specific arduino
    '''
    arduino = WebTempControl.query.get(ard_nr);
    device_type = 'web_tc';

    if not arduino:
        flash('No tempcontrols installed', 'error')
        return redirect(url_for('thermocontrol.add_webtempcontrol'));
    uform, sform, gform, iform, diff_form, wform, dform = get_wtc_forms(ard_nr);

    return render_template('change_arduino.html',
        form=uform, dform = dform, sform = sform, gform = gform, iform = iform,
        diff_form = diff_form, wform = wform, ard=arduino, device_type=device_type);

@bp.route('/update_tc', methods=['POST'])
def update_tc():
    '''
    Update the serial port.
    '''
    uform, sform, gform, iform, diff_form, wform, dform = get_tc_forms_wo_id();

    id = int(uform.id.data);
    arduino = TempControl.query.get(id);

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
        return redirect(url_for('thermocontrol.change_arduino', ard_nr = id))
    else:

        return render_template('change_arduino.html', form=uform, dform = dform,
            sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, ard=arduino);

@bp.route('/update_wtc', methods=['POST'])
def update_wtc():
    '''
    Update the ip adress.
    '''
    uform, sform, gform, iform, diff_form, wform, dform = get_wtc_forms_wo_id();

    id = int(uform.id.data);
    arduino = WebTempControl.query.get(id);

    if uform.validate_on_submit():
        ip_adress =  uform.ip_adress.data;
        port =  uform.port.data;
        print(arduino.is_alive())
        print(arduino.is_open())
        if arduino.connection_open():
            print('stop it.')
            arduino.stop();
        print('Update it.')
        arduino.ip_adress = ip_adress;
        arduino.port = port;
        db.session.commit();
        return redirect(url_for('thermocontrol.change_wtc', ard_nr = id))
    else:
        return render_template('change_arduino.html', form=uform, dform = dform,
            sform = sform, gform = gform, iform = iform, diff_form = diff_form, wform = wform, ard=arduino);

@bp.route('/serialwait_tc', methods=['POST'])
def serialwait():
    '''
    Update the serial waiting time.
    '''

    sform = UpdateSetpointForm();
    uform = UpdateForm();
    wform = SerialWaitForm()
    dform = DisconnectForm()
    gform = UpdateGainForm()
    iform = UpdateIntegralForm()
    diff_form = UpdateDifferentialForm()

    id = int(wform.id.data);
    arduino = TempControl.query.get(id);

    if wform.validate_on_submit():
        n_wait =  wform.serial_time.data;
        arduino.sleeptime = n_wait;
        db.session.commit();
        flash('We update every {} s'.format(n_wait))
        return redirect(url_for('thermocontrol.change_arduino', ard_nr = id))
    else:
        return render_template('change_arduino.html', form=uform, dform = dform,
            cform = cform,  sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, ard=arduino);

@bp.route('/wait_wtc', methods=['POST'])
def wait_wtc():
    '''
    Update the serial waiting time.
    '''
    uform, sform, gform, iform, diff_form, wform, dform = get_wtc_forms_wo_id();
    id = int(wform.id.data);
    arduino = WebTempControl.query.get(id);

    if wform.validate_on_submit():
        n_wait =  wform.serial_time.data;
        arduino.sleeptime = n_wait;
        db.session.commit();
        flash('We update every {} s'.format(n_wait))
        return redirect(url_for('thermocontrol.change_wtc', ard_nr = id))
    else:
        return render_template('change_arduino.html', form=uform, dform = dform,
            cform = cform,  sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, ard=arduino);

@bp.route('/setpoint_tc', methods=['POST'])
def arduino():
    '''
    Configure now settings for the arduino.
    '''
    sform = UpdateSetpointForm();
    uform = UpdateForm();
    wform = SerialWaitForm()
    dform = DisconnectForm()
    gform = UpdateGainForm()
    iform = UpdateIntegralForm()
    diff_form = UpdateDifferentialForm()

    id = int(sform.id.data);
    arduino = TempControl.query.get(id);

    if sform.validate_on_submit():
        arduino.setpoint = sform.setpoint.data;
        db.session.commit();
        success = arduino.set_setpoint();
        if success:
            flash('We set the setpoint to {}'.format(sform.setpoint.data))
        else:
            flash('Serial port not open.', 'error')
        return redirect(url_for('thermocontrol.change_arduino', ard_nr = id))
    else:
        return render_template('change_arduino.html', form=uform, dform = dform,
            sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, ard=arduino);

@bp.route('/setpoint_wtc', methods=['POST'])
def setpoint_wtc():
    '''
    Configure now settings for the arduino.
    '''
    uform, sform, gform, iform, diff_form, wform, dform = get_wtc_forms_wo_id();

    id = int(sform.id.data);
    arduino = WebTempControl.query.get(id);

    if sform.validate_on_submit():
        arduino.setpoint = sform.setpoint.data;
        db.session.commit();
        success = arduino.set_setpoint();
        if success:
            flash('We set the setpoint to {}'.format(sform.setpoint.data))
        else:
            flash('Setpoint not updated.', 'error')
        return redirect(url_for('thermocontrol.change_wtc', ard_nr = id))
    else:
        return render_template('change_arduino.html', form=uform, dform = dform,
            sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, ard=arduino);

@bp.route('/gain_tc', methods=['POST'])
def gain():
    '''
    Configure the new gain for the arduino.
    '''

    sform = UpdateSetpointForm();
    uform = UpdateForm();
    wform = SerialWaitForm()
    dform = DisconnectForm()
    gform = UpdateGainForm()
    iform = UpdateIntegralForm()
    diff_form = UpdateDifferentialForm()

    id = int(gform.id.data);
    arduino = TempControl.query.get(id);

    if gform.validate_on_submit():
        n_gain =  gform.gain.data;
        arduino.gain = n_gain;
        db.session.commit();
        success = arduino.set_gain();
        if success:
            flash('We set the gain to {}'.format(n_gain))
        else:
            flash('Serial port not open.', 'error')
        return redirect(url_for('thermocontrol.change_arduino', ard_nr = id))
    else:
        return render_template('change_arduino.html', form=uform, dform = dform,
            cform = cform,  sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, ard=arduino);

@bp.route('/gain_wtc', methods=['POST'])
def gain_wtc():
    '''
    Configure the new gain for the arduino.
    '''
    uform, sform, gform, iform, diff_form, wform, dform = get_wtc_forms_wo_id();
    id = int(gform.id.data);
    arduino = WebTempControl.query.get(id);

    if gform.validate_on_submit():
        n_gain =  gform.gain.data;
        arduino.gain = n_gain;
        db.session.commit();
        success = arduino.set_gain();
        if success:
            flash('We set the gain to {}'.format(n_gain))
        else:
            flash('Serial port not open.', 'error')
        return redirect(url_for('thermocontrol.change_wtc', ard_nr = id))
    else:
        return render_template('change_arduino.html', form=uform, dform = dform,
            cform = cform,  sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, ard=arduino);

@bp.route('/integral_tc', methods=['POST'])
def integral():
    '''
    Configure the new gain for the arduino.
    '''
    sform = UpdateSetpointForm();
    uform = UpdateForm();
    wform = SerialWaitForm()
    dform = DisconnectForm()
    gform = UpdateGainForm()
    iform = UpdateIntegralForm()
    diff_form = UpdateDifferentialForm()

    id = int(iform.id.data);
    arduino = TempControl.query.get(id);

    if iform.validate_on_submit():
        n_tau =  iform.tau.data;
        arduino.integral =  n_tau;
        db.session.commit();
        success = arduino.set_integral();
        if success:
            flash('We set the integration time  to {} seconds'.format(n_tau))
        else:
            flash('Serial port not open.', 'error')
        return redirect(url_for('thermocontrol.change_arduino', ard_nr = id))
    else:

        return render_template('change_arduino.html', form=uform, dform = dform,
        sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, ard = arduino);

@bp.route('/integral_wtc', methods=['POST'])
def integral_wtc():
    '''
    Configure the new gain for the arduino.
    '''
    uform, sform, gform, iform, diff_form, wform, dform = get_wtc_forms_wo_id();
    id = int(iform.id.data);
    arduino = WebTempControl.query.get(id);

    if iform.validate_on_submit():
        n_tau =  iform.tau.data;
        arduino.integral =  n_tau;
        db.session.commit();
        success = arduino.set_integral();
        if success:
            flash('We set the integration time  to {} seconds'.format(n_tau))
        else:
            flash('Serial port not open.', 'error')
        return redirect(url_for('thermocontrol.change_wtc', ard_nr = id))
    else:
        return render_template('change_arduino.html', form=uform, dform = dform,
        sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, ard = arduino);

@bp.route('/diff_tc', methods=['POST'])
def diff():
    '''
    Configure the new gain for the arduino.
    '''

    sform = UpdateSetpointForm();
    uform = UpdateForm();
    wform = SerialWaitForm()
    dform = DisconnectForm()
    gform = UpdateGainForm()
    iform = UpdateIntegralForm()
    diff_form = UpdateDifferentialForm()

    id = int(diff_form.id.data);
    arduino = TempControl.query.get(id);

    if diff_form.validate_on_submit():
        n_tau =  diff_form.tau.data;
        arduino.diff =  n_tau;
        db.session.commit();
        success = arduino.set_differential();
        if success:
            flash('We set the differentiation time  to {} seconds'.format(n_tau))
        else:
            flash('Serial port not open.', 'error')
        return redirect(url_for('thermocontrol.change_arduino', ard_nr = id))
    else:
        return render_template('change_arduino.html', form=uform, dform = dform,
            sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, ard=arduino);

@bp.route('/diff_wtc', methods=['POST'])
def diff_wtc():
    '''
    Configure the new gain for the arduino.
    '''
    uform, sform, gform, iform, diff_form, wform, dform = get_wtc_forms_wo_id();
    id = int(diff_form.id.data);
    arduino = WebTempControl.query.get(id);

    if diff_form.validate_on_submit():
        n_tau =  diff_form.tau.data;
        arduino.diff =  n_tau;
        db.session.commit();
        success = arduino.set_differential();
        if success:
            flash('We set the differentiation time  to {} seconds'.format(n_tau))
        else:
            flash('Serial port not open.', 'error')
        return redirect(url_for('thermocontrol.change_wtc', ard_nr = id))
    else:
        return render_template('change_arduino.html', form=uform, dform = dform,
            sform = sform, gform = gform, iform = iform,
            diff_form = diff_form, wform = wform, ard=arduino);

@bp.route('/save_tc/<filestring>')
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

    arduino = TempControl.query.get(id);

    if not arduino:
        flash('Aruduino not installed', 'error')
        return redirect(url_for('main.index'));

    temp = arduino.get_current_temp_value();
    param_name = 'tc' + parts[0];
    with h5py.File(filename, "a") as f:
        if 'globals' in f.keys():
            params = f['globals']
            params.attrs[param_name] = float(temp)
            flash('Added the temperature {} to the file {}'.format(temp, filename))
        else:
            flash('The file {} did not have the global group yet.'.format(filename), 'error')

    return render_template('file.html', file = filename)
