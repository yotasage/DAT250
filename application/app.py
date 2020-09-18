# flask tutorial https://code.visualstudio.com/docs/python/tutorial-flask

# imports
import os
from flask import Flask
from flask_mail import Mail

mail_settings = {
    "MAIL_SERVER": 'smtp.office365.com',
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USE_SSL": False,
    "MAIL_USERNAME": os.environ.get('MAIL_USERNAME_FLASK'),         # $Env:MAIL_USERNAME_FLASK = "username" skrives inn i Powershell for windows for å sette epost addressen serveren skal sende mail fra
    "MAIL_DEFAULT_SENDER": os.environ.get('MAIL_USERNAME_FLASK'),   # Gjør at vi ikke trenger å oppgi hvem som sender eposten, dette er default
    "MAIL_PASSWORD": os.environ.get('MAIL_PASSWORD_FLASK')          # $Env:MAIL_PASSWORD_FLASK = "password" skrives inn i Powershell for windows for å sette passorde til epost addressen serveren skal sende mail fra
}                                                                   # Disse 2 tingene er noe vi absolutt ikke vil ha i kildekoden, altså skrevet inn her med tanke på at vi pusher dette til github

# something
app = Flask(__name__)
app.config.update(mail_settings)
mail = Mail(app)
import views  # Placed here to avoid circular references, views module needs to import the app variable defined in this script.

