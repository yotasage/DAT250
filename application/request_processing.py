from datetime import datetime, timedelta
import jinja2  # For å kunne håndtere feil som 404
from flask import request, redirect, url_for, abort

from models import User, Blacklist

from app import app, db # Importerer Flask objektet app
from tools import valid_cookie, update_cookie

MAX_TIME_BETWEEN_REQUESTS = 5  # Seconds
BLOCK_PERIOD = 30  # Seconds
NUMBER_OF_FREQUENT_REQUESTS = 50

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
            db.session.commit()

    else:
        client_listing = Blacklist(ip=request.remote_addr, last=str(datetime.now()), frequent_request_count=0, wrong_password_count=0)
        db.session.add(client_listing)
        db.session.commit()

def signed_in(signed_in_page, url_page):
    if 'cookie' in request.headers:

        valid = valid_cookie(request.headers['cookie'])
        if valid == False:
            return redirect(url_for('login', timeout="True"), code=302)
        elif valid == None:
            return url_page
            
        update_cookie(request.headers['cookie'], signed_in_page)  # Øker gyldigheten av en cookie med cookie_maxAge sekunder
        return signed_in_page
    return url_page