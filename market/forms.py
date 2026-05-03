from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField,SubmitField


class RegisterForm(FlaskForm):
    username=StringField(label='user Name:')
    email_address=StringField(label='email Address:')
    password1 = PasswordField(label='password:')
    password2 = PasswordField(label="Confirm Password:")
    submit=SubmitField(label="submit")
  