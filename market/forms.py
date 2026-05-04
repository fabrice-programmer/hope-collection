from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegisterForm(FlaskForm):
    username = StringField(
        label='Username:',
        validators=[DataRequired(), Length(min=2, max=30)]
    )

    email = StringField(   # ✅ FIXED (renamed from email_address → email)
        label='Email Address:',
        validators=[DataRequired(), Email()]
    )

    password1 = PasswordField(
        label='Password:',
        validators=[DataRequired(), Length(min=6)]
    )

    password2 = PasswordField(
        label='Confirm Password:',
        validators=[DataRequired(), EqualTo('password1')]
    )

    submit = SubmitField(label="Create Account")