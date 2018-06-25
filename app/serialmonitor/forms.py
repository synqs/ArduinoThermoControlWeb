from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField,IntegerField
from wtforms.validators import DataRequired, NumberRange


class ConnectForm(FlaskForm):
    '''
    The form for connecting to the Arduino
    '''
    id = HiddenField('A hidden field');
    serial_port = StringField('Connect on port:', validators=[DataRequired()], description = 'Serial port')
    name = StringField('Name of the Arduino:', description = 'Name', default = 'Arduino')
    submit = SubmitField('Connect')

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
    id = HiddenField('A hidden field');
    serial_time = IntegerField('Time between measurements (s):', [DataRequired(), NumberRange(2,300)])
    submit = SubmitField('Update waiting time.')


class DisconnectForm(FlaskForm):
    '''
    The form for disconnecting from the Arduino
    '''
    id = HiddenField('A hidden field');
    submit = SubmitField('Disconnect')
