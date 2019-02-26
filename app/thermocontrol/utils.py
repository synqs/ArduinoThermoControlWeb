from serial.serialutil import SerialException

from app.thermocontrol.forms import ConnectForm, UpdateForm, SerialWaitForm, DisconnectForm, WebConnectForm, WebUpdateForm
from app.thermocontrol.forms import UpdateSetpointForm, UpdateGainForm, UpdateIntegralForm, UpdateDifferentialForm

from flask import flash, redirect, url_for

def start_helper(tc):
    try:
        sopen = tc.start();
        flash('Trying to start the tempcontrol')
    except SerialException as e:
        flash('SerialException: Could not open serial connection', 'error')
    return redirect(url_for('main.index'))

def get_tc_forms(ard_nr):

    uform = UpdateForm(id=ard_nr);
    sform = UpdateSetpointForm(id=ard_nr);
    gform = UpdateGainForm(id=ard_nr);
    iform = UpdateIntegralForm(id=ard_nr);
    diff_form = UpdateDifferentialForm(id=ard_nr);
    wform = SerialWaitForm(id=ard_nr);
    dform = DisconnectForm(id=ard_nr);

    return uform, sform, gform, iform, diff_form, wform, dform;

def get_tc_forms_wo_id():

    uform = UpdateForm();
    sform = UpdateSetpointForm();
    gform = UpdateGainForm();
    iform = UpdateIntegralForm();
    diff_form = UpdateDifferentialForm();
    wform = SerialWaitForm();
    dform = DisconnectForm();

    return uform, sform, gform, iform, diff_form, wform, dform;

def get_wtc_forms(ard_nr):

    uform = WebUpdateForm(id=ard_nr);
    sform = UpdateSetpointForm(id=ard_nr);
    gform = UpdateGainForm(id=ard_nr);
    iform = UpdateIntegralForm(id=ard_nr);
    diff_form = UpdateDifferentialForm(id=ard_nr);
    wform = SerialWaitForm(id=ard_nr);
    dform = DisconnectForm(id=ard_nr);

    return uform, sform, gform, iform, diff_form, wform, dform;

def get_wtc_forms_wo_id():

    uform = WebUpdateForm();
    sform = UpdateSetpointForm();
    gform = UpdateGainForm();
    iform = UpdateIntegralForm();
    diff_form = UpdateDifferentialForm();
    wform = SerialWaitForm();
    dform = DisconnectForm();

    return uform, sform, gform, iform, diff_form, wform, dform;
