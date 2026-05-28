from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, IntegerField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange
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


class RequestResetForm(FlaskForm):
    email_address = StringField(
        label='Email Address:',
        validators=[DataRequired(), Email()]
    )
    submit = SubmitField(label='Send Reset Link')


class ResetPasswordForm(FlaskForm):
    password1 = PasswordField(
        label='New Password:',
        validators=[DataRequired(), Length(min=6)]
    )

    password2 = PasswordField(
        label='Confirm New Password:',
        validators=[DataRequired(), EqualTo('password1')]
    )

    submit = SubmitField(label='Update Password')


class TestEmailForm(FlaskForm):
    to = StringField(
        label='Send To',
        validators=[DataRequired(), Email()]
    )

    subject = StringField(
        label='Subject',
        validators=[DataRequired(), Length(max=120)]
    )

    message = TextAreaField(
        label='Message',
        validators=[DataRequired(), Length(max=1000)]
    )

    submit = SubmitField(label='Send Test Email')


class TopUpForm(FlaskForm):
    amount = IntegerField(
        label='Payment Amount (RWF)',
        validators=[DataRequired(), NumberRange(min=100, message='Enter an amount of at least 100 RWF')]
    )
    payment_method = RadioField(
        label='Payment Method',
        choices=[
            ('mtn', 'MTN Mobile Money'),
            ('equity', 'Equity Bank Transfer')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField(label='Submit Payment Request')


class CheckoutForm(FlaskForm):

    sector = StringField(
        label='Sector',
        validators=[DataRequired(), Length(max=100)]
    )

    district = StringField(
        label='District',
        validators=[DataRequired(), Length(max=100)]
    )

    street = StringField(
        label='Street',
        validators=[DataRequired(), Length(max=100)]
    )

    location_note = StringField(
        label='Landmark / Additional Location Info',
        validators=[Length(max=255)]
    )

    payment_method = RadioField(
        label='Select Payment Method',
        choices=[
            ('wallet', 'Wallet balance'),
            ('mtn', 'MTN Mobile Money'),
            ('equity', 'Equity Bank Transfer')
        ],
        validators=[DataRequired()]
    )

    submit = SubmitField(label='Complete Checkout')

class ItemForm(FlaskForm):
    name = StringField(
        label='Product Name:',
        validators=[DataRequired(), Length(min=2, max=30)]
    )
    price = IntegerField(
        label='Price:',
        validators=[DataRequired(), NumberRange(min=1)]
    )
    barcode = StringField(
        label='Barcode (12 chars):',
        validators=[DataRequired(), Length(min=12, max=12)]
    )
    description = TextAreaField(
        label='Description:',
        validators=[DataRequired(), Length(max=1024)]
    )
    picture = FileField(
        label='Product Picture:',
        validators=[FileAllowed(['jpg', 'png', 'jpeg'])]
    )
    video = FileField(
        label='Product Video:',
        validators=[FileAllowed(['mp4', 'mov', 'avi'])]
    )
    submit = SubmitField(label='Save Product')

class SettingsForm(FlaskForm):
    business_name = StringField(
        label='Business Name:',
        validators=[DataRequired(), Length(max=100)]
    )
    tagline = StringField(
        label='Site Tagline / Slogan:',
        validators=[Length(max=255)]
    )
    logo_url = StringField(
        label='Logo Image URL:',
        validators=[Length(max=255)]
    )
    meta_description = TextAreaField(
        label='SEO Meta Description (for Google search):',
        validators=[Length(max=255)]
    )
    whatsapp_number = StringField(
        label='WhatsApp Number (include country code, no +):',
        validators=[DataRequired(), Length(min=10, max=15)]
    )
    contact_email = StringField(
        label='Public Contact Email:',
        validators=[DataRequired(), Email()]
    )
    business_phone = StringField(
        label='Business Phone Line:',
        validators=[Length(max=20)]
    )
    business_address = TextAreaField(
        label='Physical Store Address:',
        validators=[Length(max=255)]
    )
    facebook_url = StringField(
        label='Facebook Page URL:',
        validators=[Length(max=255)]
    )
    instagram_url = StringField(
        label='Instagram Profile URL:',
        validators=[Length(max=255)]
    )
    currency_code = StringField(
        label='Store Currency (e.g. RWF):',
        validators=[DataRequired(), Length(max=10)]
    )
    delivery_fee = IntegerField(
        label='Flat Rate Delivery Fee:',
        validators=[NumberRange(min=0)]
    )
    about_content = TextAreaField(
        label='About Us Content:',
        validators=[DataRequired()]
    )
    submit = SubmitField(label='Update Settings')
