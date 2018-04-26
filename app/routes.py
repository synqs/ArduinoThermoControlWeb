from app import app
from app.forms import ConnectForm, DataForm
import serial

from flask import render_template, flash, redirect

vals = [];
fname = '';

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    dform = DataForm()
    if dform.validate_on_submit():
        flash('We would like to submit some data locally. We have here {}'.format(vals))
        flash('We would like to submit some data remote. We have here {}'.format(app.config['REMOTE_FILE']))
        vals.append(1)
        return redirect('/index')

    lyseout = 'This is some dummy output from lyse.'
    return render_template('index.html', lyseout=fname, dform = dform)


@app.route('/config', methods=['GET', 'POST'])
def config():
    port = app.config['SERIAL_PORT']
    form = ConnectForm()

    if form.validate_on_submit():

        app.config['SERIAL_PORT'] = form.serial_port.data
        flash('We set the serial port to {}'.format(app.config['SERIAL_PORT']))
        try:
            ser = serial.Serial(form.serial_port.data, 9600, timeout = 1)
        # except serial.SerialException:
        #     s.close()
        #     ser.close()
        #     ser = serial.Serial('COM32', 9600, timeout = 1)
        except Exception as e:
             flash('{}'.format(e), 'error')
        return redirect('/index')

    return render_template('config.html', port = port, form=form)

@app.route('/file/<filename>')
def file(filename):
    dform = DataForm()
    app.config['REMOTE_FILE'] = filename;
    flash('Changed filename to {}'.format(filename))
    return redirect('/index')

@app.errorhandler(500)
def internal_error(error):
    flash('An error occured {}'.format(error), 'error')
    return render_template('500.html'), 500
