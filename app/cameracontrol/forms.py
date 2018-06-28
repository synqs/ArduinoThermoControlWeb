from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, IntegerField, FloatField, HiddenField
from wtforms.validators import DataRequired, ValidationError, NumberRange

class UpdateForm(FlaskForm):
    '''
    The form for watching another folder
    '''
    id = HiddenField('A hidden field');
    folder = StringField('Update to folder:', validators=[DataRequired()])
    submit = SubmitField('Update folder')

class RoiForm(FlaskForm):
    '''
    The form for change the ROI
    '''
    id = HiddenField('A hidden field');
    xMin = IntegerField('minimal X:', validators=[DataRequired()]);
    yMin = IntegerField('minimal Y:', validators=[DataRequired()]);
    xMax = IntegerField('maximal X:', validators=[DataRequired()]);
    yMax = IntegerField('maximal Y:', validators=[DataRequired()]);
    submit = SubmitField('Update ROI')

class ConnectForm(FlaskForm):
    '''
    The form for connecting to the camera
    '''
    id = HiddenField('A hidden field');
    folder = StringField('Folder name:', validators=[DataRequired()], description = 'Folder to watch')
    name = StringField('Name of the Camera:',validators=[DataRequired()], description = 'Name', default = 'Oven')
    submit = SubmitField('Connect')
