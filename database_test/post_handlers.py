import datetime
from flask import render_template, request, redirect, url_for 

from app import app # Importerer Flask objektet app
from tools import send_mail, is_number, random_string_generator, contain_allowed_symbols

# MIDLERTIDIGE VARIABLER SOM MÅ FJERNES FØR VI LEVERER
# BØR HELST FJERNES ETTER VI HAR FÅTT OPP BRUKER KLASSEN OG DATABASEN
username = "admin"
password = "pass"

# Denne er bare for POST forespørsler.
# Her skal vi selvfølgelig ikke bruke variablene username og password, men vi skal bruke User klassen, og sammenligne brukernavn og passord fra den.
@app.route("/<data>", methods=['POST'])  # https://flask.palletsprojects.com/en/1.1.x/quickstart/
def post_data(data = None):
    print("11")

    # Kontrollerer brukernavn og passord som er skrevet inn i login siden
    if data == "login_data":
        # Hvis en gyldig bruker skal brukeren få en session cookie, og sendes til startsiden
        if (request.form.get("uname") == username) & (request.form.get("pswd") == password):
            return redirect(url_for('startpage'), code=302)

        # Hvis ugyldig bruker, send brukeren "tilbake" til login siden, men vis en feilmelding (se html koden til login.html for hva og hvordan feilkoden vises)
        return redirect(url_for('login', error="True"), code=302)

    elif data == "verification":
        # Sjekk om den matcher med en bruker i databasen før vi setter passord og authenticator kode for brukeren.
        # Dette må gjøres for å identifisere hvem som prøver å verifisere seg.
        verification_code = request.headers['Referer'].split('verification?code=')[1].replace('&error=True', '')  # request.headers.get('Referer')
        # verification_code = request.headers['Referer'].split('verification?code=')[1].split('&')[0]  # denne funke og

        pswd = request.form['pswd']
        conf_pswd = request.form['conf_pswd']

        # Hvis passordene er like, lagre det nye passorde i databasen
        if pswd != conf_pswd:
            print(f"pswd = {pswd} != conf_pswd = {conf_pswd}")
            return redirect(url_for('verification', code=verification_code, error="True"), code=302)
        elif (8 > len(pswd) or len(pswd) > 64):
            print("password length is invalid")
            return redirect(url_for('verification', code=verification_code, error="True"), code=302)
        # Må vurdere hvilke symboler vi kan tillate, og om vi skal se etter ord/kommandoer
        elif not contain_allowed_symbols(pswd):
            print("password contains invalid characters")
            return redirect(url_for('verification', code=verification_code, error="True"), code=302)
        else:
            print(f"pswd = {pswd} == conf_pswd = {conf_pswd}")
            # Ingen feil med passorde, skal vi gjøre noe nå? Legge det inn i databasen her?
            pass

        # Hvis autentiserings greiene er good, ... fortsett

        # Hvis alt har gått greit til nå, tillatt brukeren å logge inn, 
        # altså marker som verifisert i databasen, fjern også verifiseringskoden fra databasem

    # Verifiser data fra bruker, lag bruker, sett info inn i databasen, send bekreftelsesmail.
    elif data == "registration_data":
        print(request.form)

        feedback = {'fname': '', 'mname': '', 'lname': '', 'email': '', 'id': '', 'phone_num': '', 'dob': '', 'city': '', 'postcode': '', 'address': ''}

        # Sjekker om noen av feltene er tomme, burde ikke vær mulig om nettsiden blir brukt, men kan skje om noen prøver å hacke oss
        for element in request.form:
            if request.form.get(element) == '':
                feedback[element] = "empty"

        email = request.form.get("email").split('@')
        address = request.form.get("address").split(' ')
        dob = request.form.get("dob").split('-')

        if len(dob) == 3:
            if is_number(dob[0]) and is_number(dob[1]) and is_number(dob[2]):
                try:  # Prøver å konvertere datoen fra brukeren til en dato
                    datetime.datetime(year=int(dob[2]),month=int(dob[1]),day=int(dob[0]))
                except ValueError:
                    feedback["dob"] = "invalid"
            else:
                feedback["dob"] = "invalid"
        else:
            feedback["dob"] = "invalid"

        if request.form.get("email") != '':
            if len(email) == 2:
                # Sjekk om det forran @ ikke er et tall
                if not is_number(email[0]):
                    feedback["email"] = "NaN"

                # Sjekk om det forran @ ikke har gyldig lengde
                if 6 > len(email[0]) or len(email[0]) > 7:
                    feedback["email"] = "invalidLength"

                # Sjekk om id ikke stemmer overens med epost
                if email[0] != request.form.get("id"):
                    feedback["email"] = "mismatch"
                    feedback["id"] = "mismatch"

                # Sjekker om epost addresse ikke har gyldig domene
                if email[1] != "uis.no":
                    feedback["email"] = "invalid"

        if request.form.get("id") != '':
            # Sjekker om id ikke er et tall
            if not is_number(request.form.get("id")):
                feedback["id"] = "NaN"

            # Sjekker om antall siffer i id er større enn 7 eller mindre enn 6
            if 6 > len(request.form.get("id")) or len(request.form.get("id")) > 7:
                feedback["id"] = "invalidLength"

        if request.form.get("fname") != '':
            # Sjekker om fornavn består av andre symboler enn bokstaver
            for name in request.form.get("fname").split(' '):
                print(f"Name = {name}")
                if not name.isalpha():
                    feedback["fname"] = "invalid"

        if request.form.get("mname") != '':
            # Sjekker om mellomnavn består av andre symboler enn bokstaver
            for name in request.form.get("mname").split(' '):
                print(f"Name = {name}")
                if not name.isalpha():
                    feedback["mname"] = "invalid"

        if request.form.get("lname") != '':
            # Sjekker om etternavn består av andre symboler enn bokstaver
            for name in request.form.get("lname").split(' '):
                print(f"Name = {name}")
                if not name.isalpha():
                    feedback["lname"] = "invalid"

        if request.form.get("city") != '':
            # Sjekker om by består av andre symboler enn bokstaver
            for name in request.form.get("city").split(' '):
                print(f"Name = {name}")
                if not name.isalpha():
                    feedback["city"] = "invalid"

        if not is_number(request.form.get("phone_num")) and request.form.get("phone_num") != '':
            feedback["phone_num"] = "NaN"

        if not is_number(request.form.get("postcode")) and request.form.get("postcode") != '':
            feedback["postcode"] = "NaN"

        valid = True
        for field in range(len(address) - 1):
            if not address[field].isalpha():
                valid = False
                feedback["address"] = "invalid"

        if request.form.get("address") != '' and valid:
            if len(address) >= 2:
                if not is_number(address[-1]):                      # Sjekker om gatenummer ikke er et tall
                    if len(address[-1]) >= 2:
                        if address[-1][-1].isalpha():               # Sjekker om siste symbol i gatenummeret er en bokstav, for eksempel at du bor i 3b, eller 5a
                            if not is_number(address[-1][:-1]):     # Sjekker om resten av gatenummeret uten siste symbol (bokstaven) ikke er et tall
                                feedback["address"] = "invalidNum"
                        else:
                            feedback["address"] = "invalidNum"
                    else:
                        feedback["address"] = "invalidNum"
            else:
                feedback["address"] = "invalid"

        print(feedback)

        error = False
        for element in feedback:
            if feedback[element] != '':
                error = True

        if error:
            return redirect(url_for('registration', fname=feedback["fname"], mname=feedback["mname"], lname=feedback["lname"], 
                                                    email=feedback["email"], id=feedback["id"], phone_num=feedback["phone_num"], 
                                                    dob=feedback["dob"], city=feedback["city"], postcode=feedback["postcode"], 
                                                    address=feedback["address"]), code=302)
        else:
            code = random_string_generator(128)             # Generate a random string of 128 symbols
            temp_password = random_string_generator(20)     # Generate a random string of 20 symbols
            validation_link = request.host_url + 'verification?code=' + code
            html_template = render_template('/mails/account_verification.html', fname=request.form.get("fname"), mname=request.form.get("mname"), 
                                                                                lname=request.form.get("lname"), link=validation_link,
                                                                                password=temp_password, uid=request.form.get("id"))
            
            # Denne må være med for å kunne sende bekreftelses mailen, men kan kommenteres vekk under testing
            send_mail(recipients=[request.form.get("email")], subject="Account verification", body="TEST_BODY", html=html_template)

            # Lag brukeren og før informasjonen fra registreringssiden inn i databasen, før også koden opp på brukeren

    # Hvis vi får en ugyldig POST forespørsel eller if'ene ikke sender brukeren til en spesifik side, send brukeren til fremsiden
    return redirect(url_for('index'), code=302)

# https://tedboy.github.io/flask/generated/generated/werkzeug.ImmutableMultiDict.html
# https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request
# request.form