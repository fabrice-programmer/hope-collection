import smtplib
import socket

from flask import current_app
from flask_mail import Message

from market import mail


def validate_email_config():
    mail_server = current_app.config.get('MAIL_SERVER')
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')
    sender = current_app.config.get('MAIL_DEFAULT_SENDER') or mail_username

    if mail_password:
        mail_password = ''.join(str(mail_password).split())
    password_is_placeholder = str(mail_password).lower() in {
        'abcdefghijklmnop',
        'your-16-character-app-password',
        'replace-with-your-16-character-gmail-app-password',
        'replace-with-your-gmail-app-password',
        'your-app-password'
    }
    password_has_wrong_length = bool(mail_password) and not password_is_placeholder and len(mail_password) != 16

    missing_config = []
    if not mail_server:
        missing_config.append('MAIL_SERVER')
    if not mail_username:
        missing_config.append('MAIL_USERNAME')
    if not mail_password or password_is_placeholder:
        missing_config.append('MAIL_PASSWORD')
    if not sender:
        missing_config.append('MAIL_DEFAULT_SENDER or MAIL_USERNAME')

    if missing_config:
        current_app.logger.warning('Email configuration is missing: %s', ', '.join(missing_config))
        return False, (
            f"Email configuration is missing: {', '.join(missing_config)}. "
            "Open the .env file and set MAIL_PASSWORD to your Gmail 16-character App Password."
        )
    if password_has_wrong_length:
        current_app.logger.warning('MAIL_PASSWORD has %s characters; Gmail App Passwords must have 16 characters.', len(mail_password))
        return False, (
            "MAIL_PASSWORD is not a valid Gmail App Password length. "
            "Create a Gmail App Password and paste the 16 letters into .env without spaces."
        )

    current_app.config['MAIL_PASSWORD'] = mail_password
    return True, None


def send_email(to, subject, message, html=None):
    is_valid, error_message = validate_email_config()
    if not is_valid:
        return False, error_message

    sender = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config['MAIL_USERNAME']
    email_message = Message(
        subject=subject,
        sender=('Market App', sender),
        recipients=[to],
        body=message
    )
    if html:
        email_message.html = html

    try:
        current_app.logger.info(
            'Sending email to %s using %s:%s',
            to,
            current_app.config.get('MAIL_SERVER'),
            current_app.config.get('MAIL_PORT')
        )
        mail.send(email_message)
        return True, None
    except Exception as error:
        if isinstance(error, smtplib.SMTPAuthenticationError):
            current_app.logger.exception('SMTP authentication failed')
            return False, (
                "Email login failed because Gmail rejected the username or App Password. "
                "Make sure MAIL_USERNAME is niyonsabafabrice03@gmail.com and MAIL_PASSWORD is a real "
                "16-character Gmail App Password, not your normal Gmail password."
            )
        if isinstance(error, smtplib.SMTPRecipientsRefused):
            current_app.logger.exception('SMTP recipient refused')
            return False, 'The email server rejected the recipient address.'
        if isinstance(error, (socket.gaierror, TimeoutError, smtplib.SMTPConnectError)):
            current_app.logger.exception('SMTP connection failed')
            return False, 'Could not connect to the email server. Check MAIL_SERVER, MAIL_PORT, and internet access.'

        current_app.logger.exception('Email sending failed')
        return False, f'Email delivery failed: {error}'
