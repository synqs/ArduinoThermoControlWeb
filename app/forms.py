from flask_wtf import FlaskForm
from flask_wtf.file import DataRequired, FileRequired
from wtforms import StringField, SubmitField, FileField

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class FileForm(FlaskForm):
    file = FileField('File:', validators=[FileRequired()])
    submit = SubmitField('Upload')
