# The views are the handlers that respond to requests from web browsers or other clients. 
# In Flask handlers are written as Python functions. 
# Each view function is mapped to one or more request URLs.

import datetime
import jinja2  # For å kunne håndtere feil som 404
from flask import render_template, request, redirect, url_for, abort, make_response
import string

from models import User

from app import app # Importerer Flask objektet app
from tools import send_mail, valid_cookie, update_cookie, contain_allowed_symbols


@app.route("/", methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    print("1")
    resp1 = redirect(url_for('startpage'), code=302)
    resp2 = make_response(render_template("index.html", date=datetime.datetime.now(), username="Vebjørn"))
    
    try:
        return signed_in(resp1, resp2)
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet
        abort(404)  # Returner feilmelding 404

# Denne er bare for GET forespørsler.
@app.route("/pages/login.html", methods=['GET'])
def login(page = None):
    print("2")
    resp1 = redirect(url_for('startpage'), code=302)

    messages_1 = request.args.get('error')  # Henter argumentet error fra URL som kommer med forespørselen fra nettleseren til brukeren.
    messages_2 = request.args.get('v_mail')  # Henter argumentet error fra URL som kommer med forespørselen fra nettleseren til brukeren.
    messages_3 = request.args.get('timeout')  # Henter argumentet error fra URL som kommer med forespørselen fra nettleseren til brukeren.

    resp2 = make_response(render_template("pages/login.html", date=datetime.datetime.now(), error=messages_1, v_mail=messages_2, timeout=messages_3))
    
    try:
        return signed_in(resp1, resp2)
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet
        abort(404)  # Returner feilmelding 404

@app.route("/pages/startside.html", methods=['GET'])
def startpage():
    print("3")
    resp1 = make_response(render_template("pages/startside.html", date=datetime.datetime.now()))  # Ønsket side for når vi er innlogget
    resp2 = redirect(url_for('login'), code=302)  # Side for når en ikke er innlogget
    
    try:
        return signed_in(resp1, resp2)
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet
        abort(404)  # Returner feilmelding 404

@app.route("/pages/din_side.html", methods=['GET'])
def din_side():
    print("13")
    resp1 = make_response(render_template("pages/din_side.html"))  # Ønsket side for når vi er innlogget
    resp2 = redirect(url_for('login'), code=302)  # Side for når en ikke er innlogget
    
    try:
        return signed_in(resp1, resp2)
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet
        abort(404)  # Returner feilmelding 404

@app.route("/pages/edit.html", methods=['GET'])
def edit():
    print("14")
    resp1 = make_response(render_template("pages/edit.html"))  # Ønsket side for når vi er innlogget
    resp2 = redirect(url_for('login'), code=302)  # Side for når en ikke er innlogget
    
    try:
        return signed_in(resp1, resp2)
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet
        abort(404)  # Returner feilmelding 404

# https://stackoverflow.com/questions/49547/how-do-we-control-web-page-caching-across-all-browsers
@app.route("/pages/registration.html", methods=['GET'])
def registration():
    print("4")
    resp1 = redirect(url_for('startpage'), code=302)

    # Henter argumenteer fra URL som kommer med forespørselen fra nettleseren til brukeren.
    fname = request.args.get('fname')
    mname = request.args.get('mname')
    lname = request.args.get('lname')
    email = request.args.get('email')
    uid = request.args.get('id')
    phone_num = request.args.get('phone_num')
    dob = request.args.get('dob')
    city = request.args.get('city')
    postcode = request.args.get('postcode')
    address = request.args.get('address')

    # Make_response, En alternativ måte å sende en side til brukeren, måtte gjøre det slik for å sette headers
    # trenger det ikke nå lenger siden header greiene er flyttet på, men er et greit eksempel
    resp2 = make_response(render_template("pages/registration.html", fname=fname, mname=mname, lname=lname, 
                                                                        email=email, id=uid, phone_num=phone_num, 
                                                                        dob=dob, city=city, postcode=postcode, 
                                                                        address=address))     

    try:
        return signed_in(resp1, resp2)
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet, i tilfellet noen prøver å skrive inn addresser til sider som ikke finnes
        abort(404)  # Returner feilmelding 404

@app.route("/pages/<page>", methods=['GET'])
def pages(page = None):
    print("5")
    resp1 = redirect(url_for('startpage'), code=302)  # Ønsket side for når vi er innlogget
    resp2 = make_response(render_template("pages/" + page))  # Side for når en ikke er innlogget

    try:
        return signed_in(resp1, resp2)
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet
        abort(404)  # Returner feilmelding 404

@app.route("/assets/<asset>")
def assets(asset = None):
    print("6")
    return app.send_static_file("assets/" + asset)

# Må teste om denne gjør noe
@app.route("/favicon.ico")
def favicon():
    print("7")
    return app.send_static_file("favicon.png")

@app.route("/styles/<style>")
def styles(style = None):
    print("8")
    return app.send_static_file("style/" + style)

@app.route("/verification")
def verification(style = None):
    print("9")
    verification_code = request.args.get('code')
    error = request.args.get('error')

    if contain_allowed_symbols(s=verification_code, whitelist=string.ascii_letters + string.digits):  # Kontrollerer om koden inneholder gyldige symboler før vi prøver å søke gjennom databasen med den.

        # Hent brukeren med koden i url'en, hvis det ikke er noen bruker med den koden så vil user_object = None
        user_object = User.query.filter_by(verification_code=verification_code).first()
        if user_object is not None and not user_object.verified:
            return render_template("pages/verification.html", error=error)

    return redirect(url_for('index'), code=302)

@app.route("/reset")
def reset(style = None):
    print("15")
    password_reset_code = request.args.get('code')
    error = request.args.get('error')

    if contain_allowed_symbols(s=password_reset_code, whitelist=string.ascii_letters + string.digits):  # Kontrollerer om koden inneholder gyldige symboler før vi prøver å søke gjennom databasen med den.

        # Hent brukeren med koden i url'en, hvis det ikke er noen bruker med den koden så vil user_object = None
        user_object = User.query.filter_by(password_reset_code=password_reset_code).first()
        if user_object is not None and user_object.verified:
            return render_template("pages/password_reset.html", error=error)

    return redirect(url_for('index'), code=302)

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
    print("10")
    resp.headers.set('Cache-Control', "no-cache, no-store, must-revalidate")
    resp.headers.set('Pragma', "no-cache")
    resp.headers.set('Expires', "0")
    return resp

@app.before_request
def before_request_func():
    print("16")
    print(f"request.remote_addr = {request.remote_addr}")

    # Blacklist
    # if request.remote_addr == "192.168.0.27":
    #     abort(403)


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

# https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP