from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from market.models import User


class RegisterForm(FlaskForm):

    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! please try a different username')

    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email Address already exists! please try a different email address')

    username = StringField(
        label='Username:',
        validators=[DataRequired(), Length(min=2, max=30)]
    )

    email_address = StringField(
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


# FIXED: class name must match import in routes.py (LoginForm NOT Loginform)
class LoginForm(FlaskForm):

    username = StringField(
        label='User Name:',
        validators=[DataRequired()]
    )

    password = PasswordField(
        label='Password:',
        validators=[DataRequired()]
    )

    submit = SubmitField(label='Sign In')