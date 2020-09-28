# The views are the handlers that respond to requests from web browsers or other clients. 
# In Flask handlers are written as Python functions. 
# Each view function is mapped to one or more request URLs.

import datetime
import jinja2  # For å kunne håndtere feil som 404
from flask import render_template, request, redirect, url_for, abort, make_response

from app import app # Importerer Flask objektet app
from tools import send_mail

@app.route("/", methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    print("1")
    try:
        return render_template("index.html", date=datetime.datetime.now(), username="Vebjørn")
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet
        abort(404)  # Returner feilmelding 404

# Denne er bare for GET forespørsler.
@app.route("/pages/login.html", methods=['GET'])
def login(page = None):
    print("2")
    messages = request.args.get('error')  # Henter argumentet error fra URL som kommer med forespørselen fra nettleseren til brukeren.
    try:
        return render_template("pages/login.html", date=datetime.datetime.now(), error=messages)
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet
        abort(404)  # Returner feilmelding 404

@app.route("/pages/startside.html", methods=['GET'])
def startpage():
    print("3")
    try:
        return render_template("pages/startside.html", date=datetime.datetime.now())
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet
        abort(404)  # Returner feilmelding 404

# https://stackoverflow.com/questions/49547/how-do-we-control-web-page-caching-across-all-browsers
@app.route("/pages/registration.html", methods=['GET'])
def registration():
    print("4")
    try:
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
        resp = make_response(render_template("pages/registration.html", fname=fname, mname=mname, lname=lname, 
                                                                        email=email, id=uid, phone_num=phone_num, 
                                                                        dob=dob, city=city, postcode=postcode, 
                                                                        address=address))            
                                                                                    
        # resp.headers.set('Cache-Control', "no-cache, no-store, must-revalidate")  # Flyttet dette til def add_cache_headers(resp):
        # resp.headers.set('Pragma', "no-cache")                                    # Flyttet dette til def add_cache_headers(resp):
        # resp.headers.set('Expires', "0")                                          # Flyttet dette til def add_cache_headers(resp):
        return resp
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet, i tilfellet noen prøver å skrive inn addresser til sider som ikke finnes
        abort(404)  # Returner feilmelding 404

@app.route("/pages/<page>", methods=['GET'])
def pages(page = None):
    print("5")
    try:
        return render_template("pages/" + page, date=datetime.datetime.now())
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
    messages = request.args.get('code')
    error = request.args.get('error')
    if messages == '4nkobkHIgKdtIkPavfheljs6Pig4aRu4XeTui40eSbuTFTQLluo9d13fVkUKbWESwAQDzUNB7uyPPhOFH9xONswBcAfxxZcFIkk6qm6gXRddqQCUYB2wlK1d1b8JVc75':  # Sjekk mot verifiseringskoden som vi legger i databasen
        return redirect(url_for('startpage'), code=302)
    return render_template("pages/verification.html", error=error)
    # abort(404)  # Lage custom 404 side? Tenker da med return to home knapp

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


# https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP