# flask tutorial https://code.visualstudio.com/docs/python/tutorial-flask

# imports
import os
from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

import mail_user_config  # Prøv å kjør uten denne et par ganger.    Det denne gjør er å sette variablene som leses nedenfor os.environ.get('MAIL_USERNAME_FLASK') og os.environ.get('MAIL_PASSWORD_FLASK')

cookie_maxAge = 120  # Hvor mange sekunder en cookie er gyldig
client_maxAge = 2629743  # Hvor mange sekunder en cookie skal bli bevart hos clienten, dette er omtrent en måned

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

from models import User, Cookies, Account, Transaction

# db.drop_all() # for å slette alle brukere for å teste db, bare kommentere ut når vi er ferdig

# db.create_all() # greit for å teste db, men senere så er ikke det så lurt å ha det siden den sletter alle eksisterende brukere
# når vi har integrert inn login og regin for nettsiden så burde vi fjerne db.create 
# når fila skal ut i production så skal db.create all være der enda

# Test users
# admin = User(user_id=212761, email="212761@uis.no", fname="aadmin", lname="auser", phone_num="12345678", dob="01-01-2020", city="Stavanger", postcode="4021", address="UiS", verified=1)
# guest = User(user_id=252761, email="252761@uis.no", fname="bguest", lname="buser", phone_num="12345679", dob="01-01-2020", city="Stavanger", postcode="4021", address="UiS", verified=1)

# db.session.add(admin)
# db.session.add(guest)
# db.session.commit()  # Får problemer her, sqlite3.OperationalError: table user has no column named user_id

# print(User.query.all())
# print(User.query.filter_by(user_id=212761).first())

# print(User.query.filter_by(user_id=242761).first().city)



# sudo rm /tmp/test.db
# flask run

# Placed here to avoid circular references, views module needs to import the app variable defined in this script.
import views
import post_handlers


# funker ikke å kjøre flask run i app.py
#if __name__== "__main__":
    #app.run()

# for å kjøre lagre og lese fra db skriv inn i terminal export FLASK_APP=app.py deretter flask run
