import os
from datetime import datetime, timedelta
import threading
import math
import string
import random
import pyotp
import qrcode
import json
import requests
# import time  # For testing
from flask import copy_current_request_context, redirect, url_for, request, render_template
from flask_mail import Message as _Message
from flask_sqlalchemy import SQLAlchemy
from PIL import Image, ImageFont
from io import BytesIO
# from captcha.image import ImageCaptcha
from flask_scrypt import generate_random_salt, generate_password_hash, check_password_hash


from app import app, mail, db, cookie_maxAge, client_maxAge

from app import RESTRIC_PASSWORD_RESET, PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH

from models import Cookies, Account, User, CommonPasswords

DEFAULT_RECIPIENTS = ["email@domain.com"]  # Dette er ei liste over alle default mottakere av mailen, hver mottaker skilles med komma
DOMAIN_NAME = 'jamvp.tk'
DEFAULT_MESSAGE_SUBJECT = "Flask test email, sent from server as " + os.environ.get('MAIL_USERNAME_FLASK')
TEST_BODY="text body"

Norwegian_characters = "æøåÆØÅ"

def valid_account_number(account_number):
    divided = account_number.split('.')

    if len(divided) != 3 and not contain_allowed_symbols(account_number, whitelist=string.digits + '.'):
        return False

    if not valid_number(divided[0], min_length=4, max_length=4):
        return False

    if not valid_number(divided[1], min_length=2, max_length=2):
        return False

    if not valid_number(divided[2], min_length=5, max_length=5):
        return False
    
    return True

def generate_account_numbers(amount=1, base="1337"):
    accounts = Account.query.all()
    
    account_numbers = set()
    new_account_numbers = []

    for account in accounts:
        account_numbers.add(account.account_number)

    created = 0
    while created < amount:
        suggestion = generate_account_number(base="1337")
        if suggestion not in account_numbers:
            new_account_numbers.append(suggestion)
            created += 1

    return new_account_numbers

def generate_account_number(base="1337"):
    two_digit = str(random.randint(1, 99))
    five_digit = str(random.randint(1, 99999))

    while len(two_digit) < 2:
        two_digit = "0" + two_digit

    while len(five_digit) < 5:
        five_digit = "0" + five_digit

    return base + "." + two_digit + "." + five_digit

def generate_QR(fname, id, secret_key=None, save=False):
    if secret_key is None:
        secret_key = pyotp.random_base32(length=32) # Using 256 bits secret key, see source below
    secret_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(name=(str(fname) + ', User ID: ' + str(id)), issuer_name='JAMVP Bank')
    qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
    )
    qr.add_data(secret_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    width, height = img.size
    logo_size = 80
    logo = Image.open('static/assets/logo_no_white.png')
    xmin = ymin = int((width / 2) - (logo_size / 2))
    xmax = ymax = int((width / 2) + (logo_size / 2))
    logo = logo.resize((xmax - xmin, ymax - ymin))
    img.paste(logo, (xmin, ymin, xmax, ymax))

    if save:
        img.save('qrcode_1.png')

    img_io = BytesIO()
    img.save(img_io, 'PNG', quality=100)
    img_io.seek(0)

    return secret_key, img_io

def is_human(captcha_response):
    """ Validating recaptcha response from google server
        Returns True captcha test passed for submitted form else returns False.
    """
    secret = os.environ.get('SITE_KEY')
    payload = {'response':captcha_response, 'secret':secret}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
    response_text = json.loads(response.text)
    return response_text['success']

def insertion_sort_transactions(transaction_list):
    for element in range(1, len(transaction_list)):
        index = element
        while transaction_list[index].transfer_time > transaction_list[index-1].transfer_time and index > 0:
            temp = transaction_list[index]
            transaction_list[index] = transaction_list[index-1]
            transaction_list[index-1] = temp
            index -= 1

def get_valid_cookie():
    for cookie in extract_cookies():
        valid = valid_cookie(cookie)
        if valid:
            return cookie

    return None

# Get list of cookies from cookie_header
def extract_cookies():
    if 'cookie' in request.headers:
        cookie_header = request.headers['cookie']
        cookie_header = cookie_header.replace('__Secure-sessionId=','')
        cookie_header = cookie_header.replace('sessionId=','')
        cookie_list = cookie_header.split('; ')
        return cookie_list
    return []

# Check if cookie is valid
def valid_cookie(cookie_in_question):
    if contain_allowed_symbols(s=cookie_in_question, whitelist=string.ascii_letters + string.digits):  # Kontrollerer om koden inneholder gyldige symboler før vi prøver å søke gjennom databasen med den.
        cookie = Cookies.query.filter_by(session_cookie=cookie_in_question).first()

        if cookie is None:
            return None  # Hvis cookien ikke finnes i database

        # Cookies er koblet opp mot ip til klienten, om cookie blir stjålet av noen og brukt en annen plass så får ikke "tyven" logge seg inn for det om.
        # Returnerer False, da vil cookie bli slettet en eller annen gang, og brukeren blir da også logget ut

        if 'x-forwarded-for' in request.headers:
            ip = request.headers.get('x-forwarded-for')
        else:
            ip = request.remote_addr

        if cookie.ip != ip:
            user_object = User.query.filter_by(user_id=cookie.user_id).first()

            html_template = render_template('/mails/stolen_cookie.html', fname=user_object.fname, mname=user_object.mname, 
                                                                                lname=user_object.lname, ip=ip,
                                                                                date=datetime.now())

            send_mail(recipients=[user_object.email], subject="Someone tried to sign in to your account", body="", html=html_template)
            return False
    
        # Hent ut dato og klokkeslett denne cookien er gyldig til
        valid_to = datetime.strptime(cookie.valid_to, "%Y-%m-%d %H:%M:%S.%f")

        if datetime.now() > valid_to:
            return False  # Hvis cookien er for gammel
        return True  # Hvis cookien er gyldig
    return None  # En ugyldig cookie, den inneholder ugyldige tegn, og kan derfor ikke finnes i databasen, return None

def update_cookie_clientside(cookie_in_question, resp, age=cookie_maxAge + client_maxAge):
    if "https://" in request.host_url:
        resp.headers.set('Set-Cookie', "__Secure-sessionId=" + cookie_in_question + "; Max-Age=" + str(age) + "; SameSite=Strict; Secure; HttpOnly")
    else:
        resp.headers.set('Set-Cookie', "sessionId=" + cookie_in_question + "; Max-Age=" + str(age) + "; SameSite=Strict; HttpOnly")

def update_cookie_serverside(cookie_in_question, age=cookie_maxAge + client_maxAge):
    cookie = Cookies.query.filter_by(session_cookie=cookie_in_question).first()

    if cookie is not None:
        cookie.valid_to = str(datetime.now() + timedelta(seconds=cookie_maxAge))
        db.session.commit()
        return True  # Kalrte å oppdatere cookie
    return False  # Klarte ikke å oppdatere cookie

def update_cookie(cookie_in_question, response, age=cookie_maxAge + client_maxAge):
    update_cookie_clientside(cookie_in_question, response, age)
    update_cookie_serverside(cookie_in_question, age)

# Brukes for debugging, printer ut det vi har om brukeren
def print_userdata(user_object):
    print("#################  USER DATA - START  ######################")
    print(f"id = {user_object.id}")
    print(f"user_id = {user_object.user_id}")
    print(f"email = {user_object.email}")
    print(f"fname = {user_object.fname}")
    print(f"mname = {user_object.mname}")
    print(f"lname = {user_object.lname}")
    print(f"phone_num = {user_object.phone_num}")
    print(f"dob = {user_object.dob}")
    print(f"city = {user_object.city}")
    print(f"postcode = {user_object.postcode}")
    print(f"address = {user_object.address}")
    print(f"hashed_password = {user_object.hashed_password}")
    print(f"salt = {user_object.salt}")
    print(f"verification_code = {user_object.verification_code}")
    print(f"verified = {user_object.verified}")
    print(f"password_reset_code = {user_object.password_reset_code}")
    print(f"secret_key = {user_object.secret_key}")
    print("#################  USER DATA - END  ######################")

# Må vurdere hvilke symboler vi kan tillate
def contain_allowed_symbols(s, whitelist=string.ascii_letters + string.digits + Norwegian_characters + string.punctuation):
    for c in s:
        if c not in whitelist:
            return False
    return True

def valid_date(date, separator='-'):
    if date != '':
        date = date.split(separator)  # Tar bare datoer med formatet dd-mm-yyyy, separator kan endres
        # Datoen må bestå av 3 tall
        if len(date) == 3 and (is_number(date[0]) and is_number(date[1]) and is_number(date[2])):
            try:  # Prøver å konvertere datoen fra brukeren til en dato
                datetime(year=int(date[2]),month=int(date[1]),day=int(date[0]))
            except ValueError:
                return False
        else:
            return False
    else:
        return False
    return True

# Denne kan sjekkes i en if, den gir True når den returnerer text, og False når den returnerer "".
def valid_email(mail_addr, is_num=False, min_length=6, max_length=64, check_len=False, domain='uis.no', check_domain=False):
    if mail_addr != '':
        email = mail_addr.split('@')

        if len(email) == 2 and contain_allowed_symbols(mail_addr, whitelist=string.ascii_letters + string.digits + Norwegian_characters + string.punctuation):
            
            if is_num and not is_number(email[0]):  # Sjekk om det forran @ ikke er et tall
                return "NaN"

            if check_len and (min_length > len(email[0]) or len(email[0]) > max_length):  # Sjekk om det forran @ ikke har gyldig lengde
                return "invalidLength"

            if check_domain and email[1] != domain:  # Sjekker om epost addresse ikke har gyldig domene
                return "invalid"
        else:
            return "invalid"
    else:
        return "empty"
    return ""

def valid_id(id, min_length=6, max_length=7):
    if id != '':
        if is_number(id):  # Sjekker om id er et tall
            if len(id) < 6 or len(id) > 7:  # Sjekker om antall siffer i id er mindre enn 6 eller større enn 7
                return "invalidLength"
        else:
            return "NaN"
    else:
        return "empty"
    return ""

def generate_id():
    while True:
        suggested_id = int(random_string_generator(size=6, chars=string.digits))
        if valid_id(suggested_id) and User.query.filter_by(user_id=suggested_id).first() is None:
            return suggested_id

def valid_name(names, whitelist=string.ascii_letters + Norwegian_characters):
    if names != '':
        # Sjekker om samlingen av navn (du kan ha 2 eller flere fornavn, mellomnavn (kan ha 0), etternavn) består av andre symboler enn bokstaver
        for name in names.split(' '):
            if not name.isalpha():
                if not contain_allowed_symbols(s=name, whitelist=whitelist):  # Godtar bindestrek i gatenavn
                    return "invalid"
    else:
        return "empty"
    return ""

def valid_address(address):
    # Har vi fått oppgitt en addresse?
    if address != '':
        address = address.split(' ')
    else:
        return "empty"

    # Sjekker om alle delene av addressen utenom slutten (gatenummeret), består av bokstaver.
    for field in range(len(address) - 1):
        if not address[field].isalpha():
            if not contain_allowed_symbols(s=address[field], whitelist=string.ascii_letters + '-' + Norwegian_characters):  # Godtar bindestrek i gatenavn
                return "invalid"

    # Kontrollerer at formatet og gatenummeret er gyldig
    if len(address) >= 2:
        if not is_number(address[-1]):  # Sjekker om gatenummer ikke er et tall

            # Sjekker om følgende ikke stemmer
            # Siste symbol i gatenummeret er en bokstav. For eksempel, du bor i 3b, eller 5a
            # Resten av gatenummeret uten siste symbol (bokstaven) er et tall
            if not (len(address[-1]) >= 2 and address[-1][-1].isalpha() and is_number(address[-1][:-1])):
                return "invalidNum"
    else:
        return "invalid"

    return ""

def valid_number(number, min_length=1, max_length=8):
    if is_number(number) and (min_length <= len(number) <= max_length) and '.' not in number and ',' not in number:
        return True
    return False

def valid_password(password, min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH):
        if (min_length > len(password) or len(password) > max_length):
            # print("password length is invalid")
            return False
            
        # Må vurdere hvilke symboler vi kan tillate, og om vi skal se etter ord/kommandoer
        elif not contain_allowed_symbols(password):
            # print("password contains invalid characters")
            return False

        # Hvis passorde finnes i databasen over top "10000" passord
        elif CommonPasswords.query.filter_by(password=password).first() is not None:
            return False

        # Passorde er gyldig
        return True


# https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
# https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits/23728630#23728630
def random_string_generator(size=6, chars=string.ascii_letters + string.digits):    # string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))        # Forgot to use .SystemRandom(). Using this is more cryptographically secure, this mistake was found by running bandit


def is_number(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


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

def make_user():
    user_id = 100001

    if User.query.filter_by(email="the.jona.mr@outlook.com").first() is None:

        salt = generate_random_salt()
        password_hash = generate_password_hash("adminpassword", salt)
        secret_key, qr = generate_QR("admin", str(user_id), secret_key="OEDVH3ILZSLXCZXXUVYJIUA3TU56BMWD", save=True)

        user_object = User( user_id=user_id, 
                            email="the.jona.mr@outlook.com", 
                            fname="admin", 
                            mname="",
                            lname="one", 
                            phone_num=12345678, 
                            dob="10-11-2020", 
                            city="UiS", 
                            postcode=4021, 
                            address="UiS 1", 
                            hashed_password=password_hash.decode('utf-8'),
                            salt=salt.decode('utf-8'),
                            verification_code=None,
                            verified=1,
                            secret_key=secret_key,
                            failed_logins=0,
                            last_password_reset_request=str(datetime.now() + timedelta(seconds=RESTRIC_PASSWORD_RESET)))

        account_numbers = generate_account_numbers(amount=2)
        regular_account = Account(user_id=user_id, account_number=account_numbers[0], account_name="Main", balance=58421)
        savings_account = Account(user_id=user_id, account_number=account_numbers[1], account_name="Savings", balance=3522458)

        # Legg kontoene til i databasen, og lagre alle database endringer
        db.session.add(regular_account)
        db.session.add(savings_account)

        db.session.add(user_object)
        db.session.commit()

