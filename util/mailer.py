import smtplib
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
    logger.error(app.config['BUZZN_SMTP_SERVER'])
    logger.error(app.config['BUZZN_SMTP_SERVER_PORT'])
    if app.config['BUZZN_MAILER'] == 'stdout':
        print("mailbegin>>>")
        print("receiver: {}".format(receiver))
        print(message)
        print("<<<mailend")
    elif app.config['BUZZN_MAILER'] == 'smtp':
        #context = ssl.create_default_context()
        logger.error(app.config['BUZZN_SMTP_SERVER'])
        logger.error(app.config['BUZZN_SMTP_SERVER_PORT'])
        logger.error(message)
        logger.error(type(message))
        server = smtplib.SMTP_SSL(app.config['BUZZN_SMTP_SERVER'],
                                  int(app.config['BUZZN_SMTP_SERVER_PORT']))
        server.login(app.config['BUZZN_EMAIL'],
                     app.config['BUZZN_EMAIL_PASSWORD'])
        server.sendmail(app.config['BUZZN_EMAIL'], receiver, message)
        server.close()
    else:
        raise AssertionError("BUZZN_MAILER not set, no mailer configured. Cannot send mail.")
