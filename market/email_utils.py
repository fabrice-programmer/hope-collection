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

    missing_config = []
    if not mail_server:
        current_app.logger.warning("MAIL_SERVER is not set.")
        missing_config.append('MAIL_SERVER')
    if not mail_username:
        current_app.logger.warning("MAIL_USERNAME is not set.")
        missing_config.append('MAIL_USERNAME')
    if not mail_password:
        current_app.logger.warning("MAIL_PASSWORD is not set in the environment configuration.")
        missing_config.append('MAIL_PASSWORD')
    if not sender:
        current_app.logger.warning("Email sender (MAIL_DEFAULT_SENDER) is not set.")
        missing_config.append('MAIL_DEFAULT_SENDER or MAIL_USERNAME')

    if missing_config:
        current_app.logger.warning('Email configuration is missing: %s', ', '.join(missing_config))
        is_gmail = mail_server and 'gmail' in str(mail_server).lower()
        msg = f"Email configuration is missing: {', '.join(missing_config)}."
        if is_gmail:
            msg += " Please set a 16-character App Password in your .env file."
        return False, (
            f"{msg} Check the '.env' file in your project root folder."
        )

    if password_is_placeholder:
        return False, "MAIL_PASSWORD in your .env file is still a placeholder. Please replace it with your real password."

    # Gmail specific length check
    is_gmail = mail_server and 'gmail' in str(mail_server).lower()
    if is_gmail and len(mail_password) != 16:
        return False, f"Gmail App Passwords must be exactly 16 characters. Your current password is {len(mail_password)} characters."

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
            username = current_app.config.get('MAIL_USERNAME')
            return False, (
                f"Email login failed. The server rejected the credentials for {username}. "
                "If you are using Gmail, make sure you use a 16-character App Password (not your normal password)."
            )
        if isinstance(error, smtplib.SMTPRecipientsRefused):
            current_app.logger.exception('SMTP recipient refused')
            return False, 'The email server rejected the recipient address.'
        if isinstance(error, (socket.gaierror, TimeoutError, smtplib.SMTPConnectError)):
            current_app.logger.exception('SMTP connection failed')
            return False, 'Could not connect to the email server. Check MAIL_SERVER, MAIL_PORT, and internet access.'

        current_app.logger.exception('Email sending failed')
        return False, f'Email delivery failed: {error}'
