# flask tutorial https://code.visualstudio.com/docs/python/tutorial-flask

# imports
import os
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

import random
from datetime import datetime, timedelta

import mail_user_config  # Prøv å kjør uten denne et par ganger.    Det denne gjør er å sette variablene som leses nedenfor os.environ.get('MAIL_USERNAME_FLASK') og os.environ.get('MAIL_PASSWORD_FLASK')

cookie_maxAge = 600  # Hvor mange sekunder en cookie er gyldig
client_maxAge = 2629743  # Hvor mange sekunder en cookie skal bli bevart hos clienten, dette er omtrent en måned

NUMBER_OF_LOGIN_ATTEMPTS = 10
BLOCK_LOGIN_TIME = 30

mail_settings = {
    "MAIL_SERVER": 'smtp.office365.com',
    "MAIL_PORT": 587,
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

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/database.db' # ls /tmp på terminal for å finne den, for å ha kontroll på hvor den ligger
# så kan vi lage path etter de tre /// i sqlite:////eksempelpath/tmp/test.db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import User, Cookies, Account, Transaction, Blacklist

# db.drop_all() # for å slette alle brukere for å teste db, bare kommentere ut når vi er ferdig

# db.create_all() # greit for å teste db, men senere så er ikke det så lurt å ha det siden den sletter alle eksisterende brukere
# når vi har integrert inn login og regin for nettsiden så burde vi fjerne db.create 
# når fila skal ut i production så skal db.create all være der enda


# transactions = []
# transactions.append(Transaction(transfer_time="2020-10-05 18:38:56.356743", from_acc="1442.37.37645", to_acc="1202.37.31655", message="This is fun", amount=50))
# transactions.append(Transaction(transfer_time="2020-10-03 18:38:56.356743", from_acc="1202.37.31655", to_acc="1442.37.37645", message="Savings", amount=443))
# transactions.append(Transaction(transfer_time="2020-10-02 05:38:56.356743", from_acc="1442.37.37645", to_acc="1202.37.31655", message="KID: 453453256", amount=650))
# transactions.append(Transaction(transfer_time="2020-09-05 18:38:56.356743", from_acc="1202.37.31655", to_acc="1442.37.37645", message="WOW", amount=1360))
# transactions.append(Transaction(transfer_time="2020-09-05 18:44:56.356743", from_acc="1202.37.31655", to_acc="1442.37.37645", message="Yes", amount=60))
# transactions.append(Transaction(transfer_time="2020-10-01 19:38:56.356743", from_acc="1202.37.31655", to_acc="1442.37.37645", message="Such money", amount=5000))

# transactions.append(Transaction(transfer_time="2020-10-01 12:33:56.356743", from_acc="1202.37.33333", to_acc="1442.37.37645", message="Such  74 money", amount=50300))
# transactions.append(Transaction(transfer_time="2020-10-01 02:41:56.356743", from_acc="1202.37.33333", to_acc="1442.37.37645", message="Such  5  4money", amount=54000))
# transactions.append(Transaction(transfer_time="2020-10-01 20:00:56.356743", from_acc="1202.37.33333", to_acc="1442.37.37645", message="Such 67 money", amount=50500))

# transactions.append(Transaction(transfer_time="2020-08-01 11:38:22.356743", from_acc="1202.37.31655", to_acc="1442.37.33333", message="Such  5money", amount=50010))
# transactions.append(Transaction(transfer_time="2020-11-01 19:46:33.356743", from_acc="1202.37.31655", to_acc="1442.37.33333", message="Such 44money", amount=500))
# transactions.append(Transaction(transfer_time="2019-06-11 13:00:00.356743", from_acc="1202.37.31655", to_acc="1442.37.33333", message="Such 33 money", amount=500))

# transactions.append(Transaction(transfer_time="2020-10-01 00:38:56.356743", from_acc="1202.37.31655", to_acc="1442.37.37645", message="Such  3money", amount=5080))
# transactions.append(Transaction(transfer_time="2020-07-20 01:38:56.356743", from_acc="1202.37.42311", to_acc="1442.37.37645", message="Such  2money", amount=5070))
# transactions.append(Transaction(transfer_time="2020-05-19 00:38:56.356743", from_acc="1202.37.31655", to_acc="1442.37.42311", message="Such 1 money", amount=500))

# for i in range(25):
#     date = str(datetime.now() - timedelta(seconds=random.randint(50000, 31540000)))
#     transactions.append(Transaction(transfer_time=date, from_acc="4323.12.42555", to_acc="1202.37.31655", message="Such " + str(i) + " money", amount=random.randint(50, 60000)))

# for i in range(25):
#     date = str(datetime.now() - timedelta(seconds=random.randint(50000, 31540000)))
#     transactions.append(Transaction(transfer_time=date, from_acc="1202.37.31655", to_acc="3225.35.43356", message="Such " + str(i) + " nice money", amount=random.randint(50, 60000)))

# for transaction in transactions:
#     db.session.add(transaction)
# db.session.commit()


# for account in accounts:
#     db.session.add(account)
# db.session.commit()

# Placed here to avoid circular references, views module needs to import the app variable defined in this script.
import request_processing
import views
import post_handlers
import get_handlers
import get_files
