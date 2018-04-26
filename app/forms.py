from flask_wtf import FlaskForm
from flask_wtf.file import DataRequired, FileRequired
from wtforms import StringField, SubmitField, FileField

class ConnectForm(FlaskForm):
    '''
    The form for connecting to the Arduino
    '''
    serial_port = StringField('Update to port:', validators=[DataRequired()])
    submit = SubmitField('Update port')

class DataForm(FlaskForm):
    submit = SubmitField('Submit data')
