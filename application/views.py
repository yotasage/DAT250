# The views are the handlers that respond to requests from web browsers or other clients. 
# In Flask handlers are written as Python functions. 
# Each view function is mapped to one or more request URLs.

from datetime import datetime, timedelta
import jinja2  # For å kunne håndtere feil som 404
from flask import render_template, request, redirect, url_for, abort, make_response
import string

from models import User, Blacklist, Cookies

from app import app, db # Importerer Flask objektet app
from tools import send_mail, valid_cookie, update_cookie, contain_allowed_symbols, extract_cookie
from request_processing import signed_in


@app.route("/", methods=['GET'])
def index():
    # print("1")
    resp1 = redirect(url_for('startpage'), code=302)
    resp2 = app.send_static_file("index.html")
    
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

    client_listing = Blacklist.query.filter_by(ip=request.remote_addr).first()

    if client_listing.blocked_login_until is not None and datetime.now() <= datetime.strptime(client_listing.blocked_login_until, "%Y-%m-%d %H:%M:%S.%f"):
        resp2 = make_response(render_template("pages/login.html", date=datetime.now(), error=messages_1, v_mail=messages_2, timeout=messages_3, denied=True, deactivate_btn=True))
    elif client_listing.blocked_login_until is not None:
        client_listing.blocked_login_until = None
        db.session.commit()
        resp2 = make_response(render_template("pages/login.html", date=datetime.now(), error=messages_1, v_mail=messages_2, timeout=messages_3, login=True, denied=False, deactivate_btn=False))
    else:
        resp2 = make_response(render_template("pages/login.html", date=datetime.now(), error=messages_1, v_mail=messages_2, timeout=messages_3, denied=False, deactivate_btn=False))
    
    try:
        return signed_in(resp1, resp2)
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet
        abort(404)  # Returner feilmelding 404

@app.route("/pages/startside.html", methods=['GET'])
def startpage():
    print("3")
    resp1 = make_response(render_template("pages/startside.html", date=datetime.now()))  # Ønsket side for når vi er innlogget
    resp2 = redirect(url_for('login'), code=302)  # Side for når en ikke er innlogget
    
    try:
        return signed_in(resp1, resp2)
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet
        abort(404)  # Returner feilmelding 404

@app.route("/pages/din_side.html", methods=['GET'])
def din_side():
    print("13")

    if 'cookie' in request.headers:
        cookies = request.headers['cookie']
        cookie_list = extract_cookie(cookies)
        cookie_session = cookie_list[1]
        print("YO DETTE ER EN COOKIE: " + cookie_session)
    
    cookie = Cookies.query.filter_by(session_cookie=cookie_session).first()
    if Cookies.query.filter_by(session_cookie=cookie_session).first() is not None:
        user_id_check = cookie.user_id
        user = User.query.filter_by(user_id=user_id_check).first()
    else: print("user ikke funnet")
    resp1 = make_response(render_template("pages/din_side.html", fname=user.fname, mname=user.mname, lname=user.lname,
                                        email=user.email, id=user.user_id, phone_num=user.phone_num,
                                        dob=user.dob, city=user.city, postcode=user.postcode, address=user.address))  # Ønsket side for når vi er innlogget
    resp2 = redirect(url_for('login'), code=302)  # Side for når en ikke er innlogget
    
    try:
        return signed_in(resp1, resp2)
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet
        abort(404)  # Returner feilmelding 404

    

@app.route("/pages/edit.html", methods=['GET'])
def edit():
    print("14")
    if 'cookie' in request.headers:
        cookies = request.headers['cookie']
        cookie_list = extract_cookie(cookies)
        cookie_session = cookie_list[1]
        print("YO DETTE ER EN COOKIE HÅPER JEG: " + cookie_session)
    
    cookie = Cookies.query.filter_by(session_cookie=cookie_session).first()
    if Cookies.query.filter_by(session_cookie=cookie_session).first() is not None:
        user_id_check = cookie.user_id
        user = User.query.filter_by(user_id=user_id_check).first()
    else: print("user ikke funnet")

    # Henter argumenteer fra URL som kommer med forespørselen fra nettleseren til brukeren.
    fname_error = request.args.get('fname')
    mname_error = request.args.get('mname')
    lname_error = request.args.get('lname')
    phone_num_error = request.args.get('phone_num')
    dob_error = request.args.get('dob')
    city_error = request.args.get('city')
    postcode_error = request.args.get('postcode')
    address_error = request.args.get('address')

    resp1 = make_response(render_template("pages/edit.html", fname=user.fname, mname=user.mname, lname=user.lname,
                                        email=user.email, id=user.user_id, phone_num=user.phone_num,
                                        dob=user.dob, city=user.city, postcode=user.postcode, address=user.address,
                                        fname_error=fname_error, mname_error=mname_error, lname_error=lname_error,
                                        phone_num_error=phone_num_error, dob_error=dob_error, city_error=city_error,
                                        postcode_error=postcode_error, address_error=address_error
                                        ))  # Ønsket side for når vi er innlogget
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
    # print("6")
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


# https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP