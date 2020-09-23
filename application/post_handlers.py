import datetime
from flask import render_template, request, redirect, url_for 

from app import app # Importerer Flask objektet app
from tools import send_mail

# MIDLERTIDIGE VARIABLER SOM MÅ FJERNES FØR VI LEVERER
# BØR HELST FJERNES ETTER VI HAR FÅTT OPP BRUKER KLASSEN OG DATABASEN
username = "admin"
password = "pass"

# Denne er bare for POST forespørsler.
# Her skal vi selvfølgelig ikke bruke variablene username og password, men vi skal bruke User klassen, og sammenligne brukernavn og passord fra den.
@app.route("/pages/<page>", methods=['POST'])  # https://flask.palletsprojects.com/en/1.1.x/quickstart/
def post_data(page = None):

    # Kontrollerer brukernavn og passord som er skrevet inn i login siden
    if page == "login_data":
        # Hvis en gyldig bruker skal brukeren få en session cookie, og sendes til startsiden
        if (request.form.get("uname") == username) & (request.form.get("pswd") == password):
            return redirect("startside.html", code=302)

        # Hvis ugyldig bruker, send brukeren "tilbake" til login siden, men vis en feilmelding (se html koden til login.html for hva og hvordan feilkoden vises)
        return redirect(url_for('login', error="True"), code=302)

    # Lag bruker, sett info inn i databasen, send bekreftelsesmail.
    elif page == "registration_data":
        # Hvis det er gyldig data i alle felt
        # if

        # Ellers send brukeren "tilbake" til registreringssiden, og vis en feilmelding.
        # else
        pass

    # Hvis vi får en ugyldig POST forespørsel, send brukeren til fremsiden
    return redirect(url_for('index'), code=302)

# https://tedboy.github.io/flask/generated/generated/werkzeug.ImmutableMultiDict.html
# https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request
# request.form