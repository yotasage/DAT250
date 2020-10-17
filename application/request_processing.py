from datetime import datetime, timedelta
import jinja2  # For å kunne håndtere feil som 404
from flask import render_template, request, redirect, url_for, abort

from models import User, Blacklist, Cookies

from app import app, db # Importerer Flask objektet app

# Constants
from app import MAX_TIME_BETWEEN_REQUESTS, BLOCK_PERIOD, NUMBER_OF_FREQUENT_REQUESTS

from tools import valid_cookie, update_cookie, extract_cookies, update_cookie_clientside
from tasks import delete_cookie

# https://stackoverflow.com/questions/49547/how-do-we-control-web-page-caching-across-all-browsers
# https://stackoverflow.com/questions/29464276/add-response-headers-to-flask-web-app
# Følgende HTTP Respons headers gjør at siden ikke blir lagret (cachet) av nettleseren, 
# da må siden selvfølgelig bli lastet inn fra serveren hver gang brukeren vil inn på den, og da vil ikke sensitiv informasjon for eksempel, 
# kunne bli vist me mindre brukeren er ment til å kunne se det.
#
# Disse header'ene blir nå lagt til alt som har med nettsiden å gjøre, 
# dette øker trafikken mellom serveren og brukeren (kjedelig for de me mobil data), men sikkerheten øker generelt.
@app.after_request  # Denne kjører etter route funksjonene
def add_headers(resp):
    resp.headers.set('Strict-Transport-Security', "max-age=2629743")            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security
    resp.headers.set('Cache-Control', "no-cache, no-store, must-revalidate")
    resp.headers.set('Pragma', "no-cache")
    resp.headers.set('Expires', "0")

    return resp

@app.before_request
def before_request_func():
    client_listing = Blacklist.query.filter_by(ip=request.remote_addr).first()

    if client_listing is not None:
        if client_listing.blocked_until is not None and datetime.now() <= datetime.strptime(client_listing.blocked_until, "%Y-%m-%d %H:%M:%S.%f"):
            abort(403)
        elif client_listing.blocked_until is not None:
            client_listing.blocked_until = None
            db.session.commit()

        if client_listing.blocked_until is None:
            if (datetime.now() - datetime.strptime(client_listing.last, "%Y-%m-%d %H:%M:%S.%f")).seconds <= MAX_TIME_BETWEEN_REQUESTS:
                client_listing.frequent_request_count += 1

                if client_listing.frequent_request_count >= NUMBER_OF_FREQUENT_REQUESTS:
                    client_listing.blocked_until = str(datetime.now() + timedelta(seconds=BLOCK_PERIOD))

            elif client_listing.frequent_request_count != 0:
                client_listing.frequent_request_count = 0

            client_listing.last = str(datetime.now())

    else:
        client_listing = Blacklist(ip=request.remote_addr, last=str(datetime.now()), frequent_request_count=0, wrong_password_count=0)
        db.session.add(client_listing)
        
    db.session.commit()

def signed_in(signed_in_page, url_page):
    cookie_list = extract_cookies()
    if len(cookie_list) > 0:
        
        for cookie in cookie_list:
            valid = valid_cookie(cookie)
            if valid is not None:
                break
        
        if valid == None:  # Cookiene vi fikk inn fantes ikke i databasen
            return url_page
        elif valid == False:  # En av cookiene var i databasen, og den var utgått
            cookie_object = Cookies.query.filter_by(session_cookie=cookie).first()

            if cookie_object.ip != request.remote_addr:
                resp = redirect(url_for('login'), code=302)
            else:
                resp = redirect(url_for('login', timeout="True"), code=302)

            update_cookie_clientside(cookie, resp, 0)
            delete_cookie(cookie)
            return resp
        elif valid == True:  # Fant cookien i databasen
            update_cookie(cookie, signed_in_page)  # Øker gyldigheten av en cookie med cookie_maxAge sekunder
            return signed_in_page
    return url_page  # Ingen cookies mottatt

@app.errorhandler(403)
def Forbidden(e):
    # note that we set the 403 status explicitly
    client_listing = Blacklist.query.filter_by(ip=request.remote_addr).first()
    return render_template('error/403.html', date=datetime.strptime(client_listing.blocked_until, "%Y-%m-%d %H:%M:%S.%f")), 403