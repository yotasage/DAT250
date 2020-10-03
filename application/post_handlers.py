from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
import string

from app import app, db, cookie_maxAge # Importerer Flask objektet app
from tools import send_mail, is_number, random_string_generator, contain_allowed_symbols, print_userdata
from tools import valid_date, valid_email, valid_id, valid_name, valid_address, valid_number, valid_password

from models import User, Cookies

# Denne er bare for POST forespørsler.
# Her skal vi selvfølgelig ikke bruke variablene username og password, men vi skal bruke User klassen, og sammenligne brukernavn og passord fra den.
@app.route("/<data>", methods=['POST'])  # https://flask.palletsprojects.com/en/1.1.x/quickstart/
def post_data(data = None):
    print("11")

    # Kontrollerer brukernavn og passord som er skrevet inn i login siden
    if data == "login_data":
        # Hvis en gyldig bruker skal brukeren få en session cookie, og sendes til startsiden

        user_object = User.query.filter_by(user_id=int(request.form.get("uname"))).first()

        if user_object is not None:
            print_userdata(user_object)

        if user_object is not None and (request.form.get("uname") == str(user_object.user_id)) & (request.form.get("pswd") == user_object.hashed_password) and user_object.verified:
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie
            # Cookies names starting with __Secure- must be set with the secure flag from a secure page (HTTPS)
            # A secure cookie is only sent to the server when a request is made with the https: scheme. 
            # Max-Age=<number>, Number of seconds until the cookie expires.
            # Forbids JavaScript from accessing the cookie. This mitigates attacks against cross-site scripting (XSS).

            sessionId = random_string_generator(128)
            expiration_date = datetime.now() + timedelta(seconds=cookie_maxAge)

            # datetime.strptime(date_string, format)
            # format = "%Y-%m-%d %H:%M:%S.%f"
            # datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S.%f")

            cookie = Cookies(user_id=user_object.user_id,session_cookie=sessionId, valid_to=str(expiration_date))
            db.session.add(cookie)
            db.session.commit()

            resp = make_response(redirect(url_for('startpage'), code=302))
            # resp.headers.set('__Secure-Set-Cookie', "sessionId=" + sessionId "; Max-Age=" + str(cookie_maxAge) + "; SameSite=Strict; Secure; HttpOnly")
            resp.headers.set('Set-Cookie', "sessionId=" + sessionId + "; Max-Age=" + str(cookie_maxAge) + "; SameSite=Strict; HttpOnly")
            return resp

        # Hvis ugyldig bruker, send brukeren "tilbake" til login siden, men vis en feilmelding (se html koden til login.html for hva og hvordan feilkoden vises)
        return redirect(url_for('login', error="True"), code=302)

    elif data == "verification":
        # Sjekk om den matcher med en bruker i databasen før vi setter passord og authenticator kode for brukeren.
        # Dette må gjøres for å identifisere hvem som prøver å verifisere seg.
        verification_code = request.headers['Referer'].split('verification?code=')[1].replace('&error=True', '')  # request.headers.get('Referer')

        user_object = User.query.filter_by(verification_code=verification_code).first()

        pswd = request.form['pswd']
        conf_pswd = request.form['conf_pswd']

        # Hvis passordene er like, og gyldige, lagre det nye passorde i databasen
        if pswd == conf_pswd and valid_password(pswd) and user_object is not None:
            user_object.verification_code = None
            user_object.hashed_password = pswd  # Passord skal være hashet
            user_object.salt = None  # Må ha et salt
            user_object.verified = 1
            db.session.commit()
        else:
            return redirect(url_for('verification', code=verification_code, error="True"), code=302)

        # Hvis autentiserings greiene er good, ... fortsett

        # Hvis alt har gått greit til nå, tillat brukeren å logge inn, 
        # altså marker som verifisert i databasen, fjern også verifiseringskoden fra databasen

    # Verifiser data fra bruker, lag bruker, sett info inn i databasen, send bekreftelsesmail.
    elif data == "registration_data":
        # Her legges eventuelle feilmeldinger angående dataen fra registreringssiden.
        feedback = {'fname': '', 'mname': '', 'lname': '', 'email': '', 'id': '', 'phone_num': '', 'dob': '', 'city': '', 'postcode': '', 'address': ''}

        # Er fødselsdatoen gyldig?
        if not valid_date(request.form.get("dob")):
            feedback["dob"] = "invalid"

        # Er epost gyldig?
        feedback["email"] = valid_email(request.form.get("email"))

        # Matcher bruker id og epost?
        email = request.form.get("email").split('@')
        if feedback["email"] != '' and email[0] != request.form.get("id"): # Hvis epost er gyldig, Sjekk om id ikke stemmer overens med epost
            feedback["email"] = "mismatch"
            feedback["id"] = "mismatch"

        # Er bruker id'en gyldig?
        feedback["id"] = valid_id(request.form.get("id"))

        # Er fornavn, mellomnavn og etternavn gyldig?
        feedback["fname"] = valid_name(names=request.form.get("fname"), whitelist=string.ascii_letters + '-')  # Godtar bindestrek i navn
        if request.form.get("mname") != "":  # Trenger ikke å ha mellomnavn, men hvis det har blitt skrevet inn, kontroller det.
            feedback["mname"] = valid_name(names=request.form.get("mname"))
        feedback["lname"] = valid_name(names=request.form.get("lname"))

        # Er by navn gyldig?
        feedback["city"] = valid_name(request.form.get("city"))

        # Er telefonnummer gyldig?
        if not valid_number(number=request.form.get("phone_num"), min_length=8, max_length=8):
            feedback["phone_num"] = "NaN"

        # Er post kode gyldig?
        if not valid_number(number=request.form.get("postcode"), min_length=4, max_length=4):
            feedback["postcode"] = "NaN"

        # Er addressen gyldig?
        feedback["address"] = valid_address(request.form.get("address"))

        # Har det oppstått noen feil?
        error = False
        for element in feedback:
            if feedback[element] != '':  # Hvis innholde ikke er tomt, så har det oppstått en feil
                error = True

        # Hvis det har oppstått noen feil, send brukeren "tilbake" til registreringssiden med feilmeldingene
        if error:
            return redirect(url_for('registration', fname=feedback["fname"], mname=feedback["mname"], lname=feedback["lname"], 
                                                    email=feedback["email"], id=feedback["id"], phone_num=feedback["phone_num"], 
                                                    dob=feedback["dob"], city=feedback["city"], postcode=feedback["postcode"], 
                                                    address=feedback["address"]), code=302)

        # Ellers, lag en tilfeldig link som brukeren bruker til å verifisere seg selv. Denne linken mottas på epost.
        else:
            code = random_string_generator(128)             # Generate a random string of 128 symbols, this is the verification code
            temp_password = random_string_generator(20)     # Generate a random string of 20 symbols, considering removing this
            validation_link = request.host_url + 'verification?code=' + code  # Lager linken brukeren skal få i mailen.
            html_template = render_template('/mails/account_verification.html', fname=request.form.get("fname"), mname=request.form.get("mname"), 
                                                                                lname=request.form.get("lname"), link=validation_link,
                                                                                password=temp_password, uid=request.form.get("id"))
            
            # Denne må være med for å kunne sende bekreftelses mailen, men kan kommenteres vekk under testing slik at en slipper å få så mange mailer.
            send_mail(recipients=[request.form.get("email")], subject="Account verification", body="TEST_BODY", html=html_template)

            user_object = User(   user_id=int(request.form.get("id")), 
                            email=request.form.get("email"), 
                            fname=request.form.get("fname"), 
                            mname=request.form.get("mname"),
                            lname=request.form.get("lname"), 
                            phone_num=int(request.form.get("phone_num")), 
                            dob=request.form.get("dob"), 
                            city=request.form.get("city"), 
                            postcode=int(request.form.get("postcode")), 
                            address=request.form.get("address"), 
                            verification_code=code,
                            verified=0)

            db.session.add(user_object)
            db.session.commit()

    # Verifiser data fra bruker osv
    elif data == "edit_data": 

        if 'cookie' in request.headers:
            cookie = request.headers['cookie']
            cookie = cookie.replace('sessionID=', '')
            print(cookie)

        

        # Her legges eventuelle feilmeldinger angående dataen fra registreringssiden.
        feedback = {'fname': '', 'mname': '', 'lname': '', 'phone_num': '', 'dob': '', 'city': '', 'postcode': '', 'address': ''}

        # Er fødselsdatoen gyldig?
        if not valid_date(request.form.get("dob")):
            feedback["dob"] = "invalid"

        # Er fornavn, mellomnavn og etternavn gyldig?
        feedback["fname"] = valid_name(names=request.form.get("fname"), whitelist=string.ascii_letters + '-')  # Godtar bindestrek i navn
        if request.form.get("mname") != "":  # Trenger ikke å ha mellomnavn, men hvis det har blitt skrevet inn, kontroller det.
            feedback["mname"] = valid_name(names=request.form.get("mname"))
        feedback["lname"] = valid_name(names=request.form.get("lname"))

        # Er by navn gyldig?
        feedback["city"] = valid_name(request.form.get("city"))

        # Er telefonnummer gyldig?
        if not valid_number(number=request.form.get("phone_num"), min_length=8, max_length=8):
            feedback["phone_num"] = "NaN"

        # Er post kode gyldig?
        if not valid_number(number=request.form.get("postcode"), min_length=4, max_length=4):
            feedback["postcode"] = "NaN"

        # Er addressen gyldig?
        feedback["address"] = valid_address(request.form.get("address"))

        # Har det oppstått noen feil?
        error = False
        for element in feedback:
            if feedback[element] != '':  # Hvis innholde ikke er tomt, så har det oppstått en feil
                error = True

        # Hvis det har oppstått noen feil, send brukeren "tilbake" til registreringssiden med feilmeldingene
        # if error:
        #     return redirect(url_for('registration', fname=feedback["fname"], mname=feedback["mname"], lname=feedback["lname"], 
        #                                             email=feedback["email"], id=feedback["id"], phone_num=feedback["phone_num"], 
        #                                             dob=feedback["dob"], city=feedback["city"], postcode=feedback["postcode"], 
        #                                             address=feedback["address"]), code=302)

        # # Ellers, lag en tilfeldig link som brukeren bruker til å verifisere seg selv. Denne linken mottas på epost.
        # else:
        #     db.session.commit()


    # Hvis vi får en ugyldig POST forespørsel eller if'ene ikke sender brukeren til en spesifik side, send brukeren til fremsiden
    return redirect(url_for('index'), code=302)

# https://tedboy.github.io/flask/generated/generated/werkzeug.ImmutableMultiDict.html
# https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request
# request.form