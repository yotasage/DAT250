import os
from app import app, mail
from flask_mail import Message as _Message

DEFAULT_RECIPIENTS = ["the.jona.mr@outlook.com"]  #, "232765@uis.no", "250623@uis.no", "250631@uis.no"]
DOMAIN_NAME = 'dinnettbank.tk'
DEFAULT_MESSAGE_SUBJECT = "Flask test email, sent from server as " + os.environ.get('MAIL_USERNAME_FLASK')
TEST_BODY="text body"
TEST_HTML = '<b>Test mail from the Flask server of ' + DOMAIN_NAME + ' </b><br> <br> This mail is sent from ' + os.environ.get('MAIL_USERNAME_FLASK') + ', who is a representative of ' + DOMAIN_NAME


class Message(_Message):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # work around issues with Microsoft Office365 / Outlook.com email servers
        # and their inability to handle RFC2047 encoded Message-Id headers.

        if len(self.msgId) > 77:
            # domain = current_app.config.get('MESSAGE_ID_DOMAIN', DOMAIN_NAME)  # Consider using this to get the DOMAIN_NAME
            self.msgId = self.msgId.split('@')[0] + DOMAIN_NAME + '>'  # Denne korter ned message ID slik at Office365 godtar mailen.


def send_mail(sender=None, recipients=DEFAULT_RECIPIENTS, subject=DEFAULT_MESSAGE_SUBJECT, body=TEST_BODY, html=TEST_HTML):
    # Konstruer melding
    if sender is None:
        msg = Message(subject=subject, recipients=recipients)  # Use MAIL_DEFAULT_SENDER
    else:
        msg = Message(subject=subject, sender=sender, recipients=recipients)

    # These two options can also be included within the parenthesis when making the message above
    msg.body = body  # Don't know what this is
    msg.html = html  # This is what we see when we view that mail using HTML

    # Send melding
    mail.send(msg)