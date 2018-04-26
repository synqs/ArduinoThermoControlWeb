from flask_wtf import FlaskForm
from flask_wtf.file import DataRequired, FileRequired
from wtforms import StringField, SubmitField, FileField

class LoginForm(FlaskForm):
    serial_port = StringField('Serial port of the form COM32', validators=[DataRequired()])
    submit = SubmitField('Open port')
