from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, IntegerField, FloatField
from wtforms.validators import DataRequired, ValidationError, NumberRange

class UpdateForm(FlaskForm):
    '''
    The form for connecting to the Arduino
    '''
    serial_port = StringField('Update to port:', validators=[DataRequired()])
    submit = SubmitField('Update port')

class SerialWaitForm(FlaskForm):
    '''
    The form for connecting to the Arduino
    '''
    serial_time = StringField('Time between measurements:', validators=[DataRequired()])
    submit = SubmitField('Update waiting time.')

class UpdateArduinoForm(FlaskForm):
    '''
    The form for connecting to the Arduino
    '''
    setpoint = IntegerField('New setpoint:', [DataRequired(), NumberRange(0,1023)])
    submit = SubmitField('Update setpoint')

class UpdateGainForm(FlaskForm):
    '''
    The form for connecting to the Arduino
    '''
    gain = FloatField('New gain:', [DataRequired(), NumberRange(0)])
    submit = SubmitField('Update gain')

class UpdateIntegralForm(FlaskForm):
    '''
    The form for connecting to the Arduino
    '''
    tau = FloatField('New tauI in seconds:', [DataRequired(), NumberRange(1)])
    submit = SubmitField('Update time constant')

class UpdateDifferentialForm(FlaskForm):
    '''
    The form for connecting to the Arduino
    '''
    tau = FloatField('New tauD in seconds:', [DataRequired(), NumberRange(0)])
    submit = SubmitField('Update tauD')

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
