from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
import string

from app import app, db, cookie_maxAge, client_maxAge # Importerer Flask objektet app
from tools import send_mail, is_number, random_string_generator, contain_allowed_symbols, print_userdata, Norwegian_characters
from tools import update_cookie_clientside, get_valid_cookie
from tasks import delete_cookie

from models import User, Cookies, Blacklist

NUMBER_OF_LOGIN_ATTEMPTS = 10
BLOCK_LOGIN_TIME = 30

# Denne er bare for GET forespørsler.
@app.route("/<data>", methods=['GET'])  # https://flask.palletsprojects.com/en/1.1.x/quickstart/
def get_data(data = None):
    print("21")

    if data == "logout":
        session_cookie = get_valid_cookie()  # Henter gyldig cookie fra headeren hvis det er en
        print(f"logout - {session_cookie}")
        if session_cookie is not None:  # Om vi fikk en gyldig header
            resp = redirect(url_for('login'), code=302)
            delete_cookie(session_cookie)
            update_cookie_clientside(session_cookie, resp, 0)
            return resp


    return redirect(url_for('index'), code=302)