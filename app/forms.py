from flask_wtf import FlaskForm
from flask_wtf.file import DataRequired, FileRequired
from wtforms import StringField, SubmitField, FileField

class UpdateForm(FlaskForm):
    '''
    The form for connecting to the Arduino
    '''
    serial_port = StringField('Update to port:', validators=[DataRequired()])
    submit = SubmitField('Update port')

class UpdateArduinoForm(FlaskForm):
    '''
    The form for connecting to the Arduino
    '''
    setpoint = StringField('New setpoint:', validators=[DataRequired()])
    submit = SubmitField('Update setpoint')


class DisconnectForm(FlaskForm):
    '''
    The form for disconnecting from the Arduino
    '''
    submit = SubmitField('Disconnect')

class ConnectForm(FlaskForm):
    '''
    The form for disconnecting from the Arduino
    '''
    submit = SubmitField('Connect')

class DataForm(FlaskForm):
    submit = SubmitField('Submit data')
