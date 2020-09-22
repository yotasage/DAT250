import os
import datetime
import threading
# import time  # For testing
from flask import copy_current_request_context
from flask_mail import Message as _Message

from application.app import app, mail

DEFAULT_RECIPIENTS = ["email@domain.com"]  # Dette er ei liste over alle default mottakere av mailen, hver mottaker skilles med komma
DOMAIN_NAME = 'dinnettbank.tk'
DEFAULT_MESSAGE_SUBJECT = "Flask test email, sent from server as " + os.environ.get('MAIL_USERNAME_FLASK')
TEST_BODY="text body"


class Message(_Message):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # work around issues with Microsoft Office365 / Outlook.com email servers
        # and their inability to handle RFC2047 encoded Message-Id headers.

        if len(self.msgId) > 77:
            # domain = current_app.config.get('MESSAGE_ID_DOMAIN', DOMAIN_NAME)  # Consider using this to get the DOMAIN_NAME
            self.msgId = self.msgId.split('@')[0] + DOMAIN_NAME + '>'  # Denne korter ned message ID slik at Office365 godtar mailen.


def test_html_constructor():
    TEST_HTML = (   '<b>Test mail from the Flask server of ' + DOMAIN_NAME + 
                    ' </b><br> <br> This mail is sent from ' + os.environ.get('MAIL_USERNAME_FLASK') + 
                    ', who is a representative of ' + DOMAIN_NAME + 
                    '<br><br> This mail was sent ' + str(datetime.datetime.now())) 
    return TEST_HTML


def send_mail(sender=None, recipients=DEFAULT_RECIPIENTS, subject=DEFAULT_MESSAGE_SUBJECT, body=TEST_BODY, html=None):

    # This function is run in a separate thread to send emails.
    # This will reduce the load on the main thread/program so that the responsiveness of the server is maintained.
    # Sending a mail typically took 1 second for the send_mail function, now it takes 0.001 seconds typically. Used time.time() to find the time spent on sending the email
    @copy_current_request_context
    def mail_sender_thread(msg):
        mail.send(msg)

    # Konstruer melding
    if sender is None:
        msg = Message(subject=subject, recipients=recipients)  # Use MAIL_DEFAULT_SENDER as sender
    else:
        msg = Message(subject=subject, sender=sender, recipients=recipients)

    # The following two options (body and html) can also be included within the parenthesis when making the message above
    msg.body = body  # Don't know what this is

    if html is None:
        msg.html = test_html_constructor()
    else:
        msg.html = html  # This is what we see when we view the mail using HTML

    # Send melding
    mail_sending_thread = threading.Thread(target=mail_sender_thread, args=(msg,))
    mail_sending_thread.start()

