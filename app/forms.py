from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, IntegerField, FloatField, HiddenField
from wtforms.validators import DataRequired, ValidationError, NumberRange

class UpdateForm(FlaskForm):
    '''
    The form for connecting to the Arduino
    '''
    id = HiddenField('A hidden field');
    serial_port = StringField('Update to port:', validators=[DataRequired()])
    submit = SubmitField('Update port')

class SerialWaitForm(FlaskForm):
    '''
    The form for connecting to the Arduino
    '''
    serial_time = StringField('Time between measurements:', validators=[DataRequired()])
    submit = SubmitField('Update waiting time.')

class UpdateSetpointForm(FlaskForm):
    '''
    The form for connecting to the Arduino
    '''
    id = HiddenField('A hidden field');
    setpoint = IntegerField('New setpoint:', [DataRequired(), NumberRange(0,1023)])
    submit = SubmitField('Update setpoint')

class UpdateGainForm(FlaskForm):
    '''
    The form for updateing the gain of the Arduino
    '''
    id = HiddenField('A hidden field');
    gain = FloatField('New gain:', [DataRequired(), NumberRange(0)])
    submit = SubmitField('Update gain')

class UpdateIntegralForm(FlaskForm):
    '''
    The form for updating the integral part to the Arduino
    '''
    id = HiddenField('A hidden field');
    tau = FloatField('New tauI in seconds:', [DataRequired(), NumberRange(1)])
    submit = SubmitField('Update time constant')

class UpdateDifferentialForm(FlaskForm):
    '''
    The form for updating the differential part of the Arduino
    '''
    id = HiddenField('A hidden field');
    tau = FloatField('New tauD in seconds:', [DataRequired(), NumberRange(0)])
    submit = SubmitField('Update tauD')

class DisconnectForm(FlaskForm):
    '''
    The form for disconnecting from the Arduino
    '''
    id = HiddenField('A hidden field');
    submit = SubmitField('Disconnect')

class ConnectForm(FlaskForm):
    '''
    The form for connecting to the Arduino
    '''
    id = HiddenField('A hidden field');
    serial_port = StringField('Connect on port:', validators=[DataRequired()], description = 'Serial port')
    name = StringField('Name of the Arduino:', description = 'Name', default = 'Arduino')
    submit = SubmitField('Connect')

class ReConnectForm(FlaskForm):
    '''
    The form for recconnecting to the Arduino
    '''
    id = HiddenField('A hidden field');
    submit = SubmitField('Connect')
