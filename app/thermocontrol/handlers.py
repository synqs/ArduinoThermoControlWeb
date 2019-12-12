from app.thermocontrol import bp
from app.thermocontrol.forms import ConnectForm, UpdateForm, SerialWaitForm, DisconnectForm, WebConnectForm
from app.thermocontrol.forms import UpdateSetpointForm, UpdateGainForm, UpdateIntegralForm, UpdateDifferentialForm
from app.thermocontrol.models import WebTempControl, wtc_schema, wtcs_schema
from app.thermocontrol.utils import start_helper, get_wtc_forms, get_wtc_forms_wo_id
from app.thermocontrol.utils import get_tc_forms, get_tc_forms_wo_id

from app import socketio, db

from flask import render_template, flash, redirect, url_for, session, jsonify, request
from flask_login import login_required, current_user

@bp.route('/wtc/')
@login_required
def all_wtcs():
    '''
    Read the properties of the arduino.
    '''
    wtcs = WebTempControl.query.all();
    return jsonify({
        'status': 'success',
        'wtcs': wtcs_schema.dump(wtcs)
        })

@bp.route('/wtc/<int:ard_nr>', methods=['GET', 'PUT'])
@login_required
def single_wtc(ard_nr):
    '''
    Read the properties of the arduino.
    '''
    response_object = {'status': 'success'};
    if request.method == 'GET':
        arduino = WebTempControl.query.get(ard_nr);
        arduino.pull_arduino();
        return jsonify({'status': 'success', 'wtc':wtc_schema.dump(arduino)});
    elif request.method == 'PUT':
        post_data = request.get_json();
        arduino = WebTempControl.query.get(ard_nr);
        success = True;
        for key in post_data.keys():
            if key == 'setpoint':
                setattr(arduino, key, float(post_data[key]));
                success = arduino.set_setpoint();
            else:
                setattr(arduino, key, post_data[key]);
        if success:
            db.session.commit();
        response_object['message'] = 'Arduino updated!'
    return jsonify(response_object);

@bp.route('/details_wtc/<int:ard_nr>', methods=['GET', 'POST'])
@login_required
def details_wtc(ard_nr):
    '''
    The main function for rendering the principal site.
    '''
    arduino = WebTempControl.query.get(ard_nr);

    device_type = 'web_tc';

    if not arduino:
        flash('No tempcontrols installed', 'error')
        return redirect(url_for('thermocontrol.add_webtempcontrol'));


    if not current_user.id == arduino.user_id:
        flash('Access denied', 'error')
        return redirect(url_for('main.index'));
    print(arduino.id)
    return render_template('details.html', ard=arduino,
        device_type=device_type, is_log = True);

@bp.route('/add_webtempcontrol', methods=['GET', 'POST'])
@login_required
def add_webtempcontrol():
    '''
    Add an arduino with ethernet interface to the set up
    '''
    cform = WebConnectForm();
    device_type = 'web_tc';
    if cform.validate_on_submit():
        ip_adress = cform.ip_adress.data;
        port = cform.port.data;
        name = cform.name.data;
        if not port:
            port = 80;
        tc = WebTempControl(name=name, ip_adress= ip_adress, port = port,
        user_id = current_user.id, sleeptime=3);

        db.session.add(tc);
        db.session.commit();
        flash('We added a new arduino {}'.format(name))
        return redirect(url_for('main.index'))

    tempcontrols = WebTempControl.query.all();
    n_ards = len(tempcontrols)
    return render_template('add_webarduino.html', cform = cform, n_ards=n_ards,
    device_type = device_type);

@bp.route('/remove_wtc/<int:ard_nr>')
@login_required
def remove_wtc(ard_nr):
    tc = WebTempControl.query.get(ard_nr);
    db.session.delete(tc)
    db.session.commit()

    flash('Removed the web temperature control # {}.'.format(ard_nr));
    return redirect(url_for('main.index'))

@bp.route('/start_wtc/<int:ard_nr>')
@login_required
def start_wtc(ard_nr):
    '''
    The main function for rendering the principal site.
    '''
    tc = WebTempControl.query.get(ard_nr);
    return start_helper(tc);

@bp.route('/stop_wtc/<int:ard_nr>')
@login_required
def stop_wtc(ard_nr):
    '''
    The main function for rendering the principal site.
    '''
    tc = WebTempControl.query.get(ard_nr);
    tc.stop()
    flash('Stopped the thermocontrol')
    socketio.emit('close_conn',{'data': tc.conn_str()})
    return redirect(url_for('main.index'))


@bp.route('/update_wtc', methods=['POST'])
@login_required
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
        if arduino.connection_open():
            arduino.stop();
        arduino.ip_adress = ip_adress;
        arduino.port = port;
        db.session.commit();
        return redirect(url_for('thermocontrol.change_wtc', ard_nr = id))
    else:
        return render_template('change_arduino.html', form=uform, dform = dform,
            sform = sform, gform = gform, iform = iform, diff_form = diff_form, wform = wform, ard=arduino);

@bp.route('/wait_wtc', methods=['POST'])
@login_required
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

@bp.route('/gain_wtc', methods=['POST'])
@login_required
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

@bp.route('/integral_wtc', methods=['POST'])
@login_required
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

@bp.route('/diff_wtc', methods=['POST'])
@login_required
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
