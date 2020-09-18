from app import app, mail
from flask_mail import Message

subject = "test flask, mail sent by server"
recipients = ["the.jona.mr@outlook.com"]  #, "232765@uis.no", "250623@uis.no", "250631@uis.no"]
DOMAIN_NAME = 'dinnettbank.tk'

def send_mail(recipients=recipients, subject=subject):
    msg = Message(subject=subject, recipients=recipients)
    msg.body = 'text body'
    msg.html = '<b>HTML</b> body, sent by the Flask server. <br> <br> This mail is now sent on the domain of UiS. <br> <br> Denne mailen skal bli sendt til Pholit og Alide og Martin'

    msg.msgId = msg.msgId.split('@')[0] + DOMAIN_NAME + '>'  # Denne korter ned message ID slik at Office365 godtar mailen.

    mail.send(msg)