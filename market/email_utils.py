import socket
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

from flask import current_app


def send_email(to, subject, message):
    mail_server = current_app.config.get('MAIL_SERVER')
    mail_port = current_app.config.get('MAIL_PORT', 587)
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')
    sender = current_app.config.get('MAIL_DEFAULT_SENDER') or mail_username
    use_tls = current_app.config.get('MAIL_USE_TLS', True)
    use_ssl = current_app.config.get('MAIL_USE_SSL', False)

    if mail_password:
        mail_password = ''.join(str(mail_password).split())
    password_is_placeholder = str(mail_password).lower() in {
        'your-16-character-app-password',
        'replace-with-your-gmail-app-password',
        'your-app-password'
    }

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

    email_message = MIMEText(message, 'plain', 'utf-8')
    email_message['From'] = formataddr(('Market App', sender))
    email_message['To'] = to
    email_message['Subject'] = subject

    try:
        current_app.logger.info('Sending email to %s using %s:%s', to, mail_server, mail_port)
        if use_ssl:
            server = smtplib.SMTP_SSL(mail_server, mail_port, timeout=15)
        else:
            server = smtplib.SMTP(mail_server, mail_port, timeout=15)

        with server as smtp:
            smtp.ehlo()
            if use_tls and not use_ssl:
                smtp.starttls()
                smtp.ehlo()
            smtp.login(mail_username, mail_password)
            smtp.sendmail(sender, [to], email_message.as_string())

        return True, None
    except smtplib.SMTPAuthenticationError as error:
        current_app.logger.error('SMTP authentication failed: %s', error)
        return False, 'Email login failed. For Gmail, use your Gmail address and a 16-character App Password.'
    except smtplib.SMTPRecipientsRefused as error:
        current_app.logger.error('SMTP recipient refused: %s', error)
        return False, 'The email server rejected the recipient address.'
    except (socket.gaierror, TimeoutError, smtplib.SMTPConnectError) as error:
        current_app.logger.error('SMTP connection failed: %s', error)
        return False, 'Could not connect to the email server. Check MAIL_SERVER, MAIL_PORT, and internet access.'
    except Exception as error:
        current_app.logger.error('Email sending failed: %s', error)
        return False, 'Email delivery failed. Check your SMTP settings and try again.'
