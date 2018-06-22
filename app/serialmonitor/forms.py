from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired

class ConnectForm(FlaskForm):
    '''
    The form for connecting to the Arduino
    '''
    id = HiddenField('A hidden field');
    serial_port = StringField('Connect on port:', validators=[DataRequired()], description = 'Serial port')
    name = StringField('Name of the Arduino:', description = 'Name', default = 'Arduino')
    submit = SubmitField('Connect')
