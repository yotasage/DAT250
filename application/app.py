# flask tutorial https://code.visualstudio.com/docs/python/tutorial-flask

# imports
import os
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

import random
from datetime import datetime, timedelta

import mail_user_config  # Prøv å kjør uten denne et par ganger.    Det denne gjør er å sette variablene som leses nedenfor os.environ.get('MAIL_USERNAME_FLASK') og os.environ.get('MAIL_PASSWORD_FLASK')

COOKIE_MAXAGE = cookie_maxAge = 900  # Hvor mange sekunder en cookie er gyldig
CLIENT_MAXAGE = client_maxAge = 2629743  # Hvor mange sekunder en cookie skal bli bevart hos clienten, dette er omtrent en måned

NUMBER_OF_LOGIN_ATTEMPTS_IP = 100
BLOCK_LOGIN_TIME_IP = 60*60*24

NUMBER_OF_LOGIN_ATTEMPTS_USER = 10
BLOCK_LOGIN_TIME_USER = 60*60

RESTRIC_PASSWORD_RESET = 60 #60*30

MAX_TIME_BETWEEN_REQUESTS = 2  # Seconds, if a request is performed within a certain amount of time after another, it is considered too frequent
BLOCK_PERIOD = 60*60*24  # Seconds
NUMBER_OF_FREQUENT_REQUESTS = 1000

PASSWORD_MAX_LENGTH = 128
PASSWORD_MIN_LENGTH = 8

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',  # smtp.office365.com
    "MAIL_PORT": 587,  # Use port 465, or port 587 if your client begins with plain text before issuing the STARTTLS command.
    "MAIL_USE_TLS": True,                                           # Mail blir kryptert
    "MAIL_USE_SSL": False,                                          # Dette er en annen krypterings greie vi ikke bruker
    "MAIL_USERNAME": os.environ.get('MAIL_USERNAME_FLASK'),         # $Env:MAIL_USERNAME_FLASK = "username" skrives inn i Powershell for windows                                                    # os.environ.get('MAIL_USERNAME_FLASK')
                                                                    # for å sette epost addressen serveren skal sende mail fra, bruk studentmailen din, for eksempel studentnummer@uis.no
    "MAIL_DEFAULT_SENDER": os.environ.get('MAIL_USERNAME_FLASK'),   # Gjør at vi ikke trenger å oppgi hvem som sender eposten, dette er default
    "MAIL_PASSWORD": os.environ.get('MAIL_PASSWORD_FLASK')          # $Env:MAIL_PASSWORD_FLASK = "password" skrives inn i Powershell for windows                                                    # os.environ.get('MAIL_PASSWORD_FLASK')
                                                                    # for å sette passorde til epost addressen serveren skal sende mail fra, bruk feide passorde ditt
}                                                                   # Disse 2 tingene (mail og passord, i hvert fall passord) er noe vi absolutt ikke vil ha (hardcoded) 
                                                                    # i kildekoden, altså skrevet inn her med tanke på at vi pusher dette til github. Derfor bruker vi environment variabler

app = Flask(__name__)
app.config.update(mail_settings)
mail = Mail(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import User, Cookies, Account, Transaction, Blacklist, CommonPasswords

# db.drop_all() # for å slette alle brukere for å teste db, bare kommentere ut når vi er ferdig

# db.create_all() # greit for å teste db, men senere så er ikke det så lurt å ha det siden den sletter alle eksisterende brukere
# når vi har integrert inn login og regin for nettsiden så burde vi fjerne db.create 
# når fila skal ut i production så skal db.create all være der enda


if len(CommonPasswords.query.all()) == 0:

    r_file_1 = open('application/bad_password_2.txt', 'r')

    namelist_1 = []

    line = r_file_1.readline()
    while not line == '':
        line = line.replace('\n', '')
        if len(line) >= PASSWORD_MIN_LENGTH:
            namelist_1.append(line)
            db.session.add(CommonPasswords(password=line))
        line = r_file_1.readline()

    print(len(namelist_1))

    print(len(CommonPasswords.query.all()))

    print(CommonPasswords.query.filter_by(password="fatluvr69").first())

db.session.commit()

# Placed here to avoid circular references, views module needs to import the app variable defined in this script.
import request_processing
import views
import post_handlers
import get_handlers
import get_files


