from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField,FileField,SubmitField, TextAreaField,validators,SelectField,SelectMultipleField
from wtforms.widgets import TextArea, html5
from wtforms.fields.html5 import DateField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, Length

class UploadForm(FlaskForm):
    fileName=FileField("Upload your Video here",validators=[DataRequired()])
    submit=SubmitField('Upload')
