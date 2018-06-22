from app import app, socketio

from app.serialmonitor import bp
from app.serialmonitor.forms import ConnectForm

from app.serialmonitor.models import SerialArduinoMonitor, serialmonitors

from flask import render_template, flash, redirect, url_for, session

@bp.route('/add_serialmonitor', methods=['GET', 'POST'])
def add_serialmonitor():
    '''
    Add an arduino to the set up
    '''
    global serialmonitors;
    cform = ConnectForm();

    if cform.validate_on_submit():
        n_port =  cform.serial_port.data;
        name = cform.name.data;
        ssProto = SerialArduinoMonitor(socketio, name);
        ssProto.id = len(serialmonitors);
        try:
            ssProto.open_serial(n_port, 9600, timeout = 1)
            ssProto.start()
            if ssProto.is_open():
                app.config['SERIAL_PORT'] = n_port;
                serialmonitors.append(ssProto)
                flash('We added a new arduino {}'.format(app.config['SERIAL_PORT']))
                return redirect(url_for('main.index'))
            else:
                 flash('Adding the Arduino went wrong', 'error')
                 return redirect(url_for('serialmonitor.add_serialmonitor'))
        except Exception as e:
             flash('{}'.format(e), 'error')
             return redirect(url_for('serialmonitor.add_serialmonitor'))

    port = app.config['SERIAL_PORT']
    n_ards = len(serialmonitors)
    return render_template('add_arduino.html', port = port, cform = cform, n_ards=n_ards,
    device_type = 'serial monitor');
