import smtplib
from email.mime.text import MIMEText
from email.header import Header
import logging.config

from flask import current_app as app


logger = logging.getLogger(__name__)


def send_mail(receiver, message, subject):
    """Sends a new mail to the given receiver.
    :param str receiver: The receiver's mail address.
    :param str message: The message.
    :param str subject: The subject of the mail.
    :raises AssertionError: If no mailer is configured i.e. BUZZN_MAILER is not
    set.
    """

    if app.config['BUZZN_MAILER'] == 'stdout':
        print("mailbegin>>>")
        print("receiver: {}".format(receiver))
        print(message)
        print("<<<mailend")
    elif app.config['BUZZN_MAILER'] == 'smtp':
        with smtplib.SMTP_SSL(app.config['BUZZN_SMTP_SERVER'],
                              app.config['BUZZN_SMTP_SERVER_PORT']) as server:
            msg = MIMEText(message, 'plain', 'utf-8')
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = app.config['BUZZN_EMAIL']
            msg['To'] = receiver
            server.login(app.config['BUZZN_EMAIL'],
                         app.config['BUZZN_EMAIL_PASSWORD'])
            server.send_message(msg)
        logger.info("Password reset message sent.")
    else:
        raise AssertionError("BUZZN_MAILER not set, no mailer configured. Cannot send mail.")
