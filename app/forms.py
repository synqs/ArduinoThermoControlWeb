from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, IntegerField
from wtforms.validators import DataRequired, ValidationError, NumberRange

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
    setpoint = IntegerField('New setpoint:', [DataRequired(), NumberRange(0,1023)])
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
