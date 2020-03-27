import smtplib
import ssl
import logging.config

from flask import current_app as app

logger = logging.getLogger(__name__)


def send_mail(receiver, message):
    """Sends a new mail to the given receiver.
    :param str receiver: The receiver's mail address.
    :param str message: The message.
    :raises AssertionError: If no mailer is configured i.e. BUZZN_MAILER is not
    set.
    """

    if app.config['BUZZN_MAILER'] == 'stdout':
        print("mailbegin>>>")
        print("receiver: {}".format(receiver))
        print(message)
        print("<<<mailend")
    elif app.config['BUZZN_MAILER'] == 'smtp':
        context = ssl.create_default_context()
        message_as_bytes = message.encode('ascii', 'xmlcharrefreplace')
        with smtplib.SMTP_SSL(app.config['BUZZN_SMTP_SERVER'],
                              app.config['BUZZN_SMTP_SERVER_PORT'],
                              context=context) as server:
            server.login(app.config['BUZZN_EMAIL'],
                         app.config['BUZZN_EMAIL_PASSWORD'])
            server.sendmail(app.config['BUZZN_EMAIL'], receiver, message_as_bytes)
        logger.info("Password reset message sent.")
    else:
        raise AssertionError("BUZZN_MAILER not set, no mailer configured. Cannot send mail.")
