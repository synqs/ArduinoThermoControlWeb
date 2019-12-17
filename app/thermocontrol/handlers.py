from app.thermocontrol import bp
from app.thermocontrol.forms import ConnectForm, UpdateForm, SerialWaitForm, DisconnectForm, WebConnectForm
from app.thermocontrol.forms import UpdateSetpointForm, UpdateGainForm, UpdateIntegralForm, UpdateDifferentialForm
from app.thermocontrol.models import WebTempControl, wtc_schema, wtcs_schema

from app import db

from flask import render_template, flash, redirect, url_for, session, jsonify, request
from flask_login import login_required, current_user

@bp.route('/wtc/', methods=['GET', 'POST'])
@login_required
def all_wtcs():
    '''
    Read the properties of the arduino.
    '''
    response_object = {'status': 'success'};
    if request.method == 'GET':
        wtcs = WebTempControl.query.all();
        response_object['wtcs'] = wtcs_schema.dump(wtcs);
        return jsonify(response_object);
    elif request.method == 'POST':
        post_data = request.get_json();
        ip_adress = post_data.get('ip_adress');
        port = post_data.get('port');
        name = post_data.get('name');
        if not port:
            port = 80;
        tc = WebTempControl(name=name, ip_adress= ip_adress, port = port,
        user_id = current_user.id, sleeptime=3);

        db.session.add(tc);
        db.session.commit();
        return redirect(url_for('main.index'))


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

@bp.route('/start/wtc/<int:ard_nr>')
@login_required
def start_wtc(ard_nr):
    '''
    The start function for the arduino
    '''
    tc = WebTempControl.query.get(ard_nr);
    sopen = tc.start();
    return jsonify({'status': 'success', 'wtc': wtc_schema.dump(tc)});

@bp.route('/stop/wtc/<int:ard_nr>')
@login_required
def stop_wtc(ard_nr):
    '''
    The stop function for the arduino
    '''
    tc = WebTempControl.query.get(ard_nr);
    tc.stop()
    return jsonify({'status': 'success', 'wtc':wtc_schema.dump(tc)});

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
    return redirect(url_for('main.index'));
