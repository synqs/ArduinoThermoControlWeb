from app import app
from app.forms import LoginForm
import serial
from flask import render_template, flash, redirect

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = LoginForm()

    if form.validate_on_submit():
        flash('We got the following port {}'.format(form.serial_port.data))
        try:
            ser = serial.Serial('COM32', 9600, timeout = 1)
        # except serial.SerialException:
        #     s.close()
        #     ser.close()
        #     ser = serial.Serial('COM32', 9600, timeout = 1)
        except Exception as e:
             flash('{}'.format(e), 'error')
        return redirect('/index')

    lyseout = 'This is some dummy output from lyse.'
    return render_template('index.html', lyseout=lyseout, form=form)


@app.errorhandler(500)
def internal_error(error):
    flash('An error occured {}'.format(error), 'error')
    return render_template('500.html'), 500
