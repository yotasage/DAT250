# The views are the handlers that respond to requests from web browsers or other clients. 
# In Flask handlers are written as Python functions. 
# Each view function is mapped to one or more request URLs.

from datetime import datetime, timedelta
import jinja2  # For å kunne håndtere feil som 404
from flask import render_template, request, redirect, url_for, abort, make_response, send_file
import string

from models import User, Blacklist, Cookies, Account, Transaction

from app import app, db, cookie_maxAge # Importerer Flask objektet app
from tools import send_mail, valid_cookie, update_cookie, contain_allowed_symbols, extract_cookies, get_valid_cookie, insertion_sort_transactions, valid_account_number, generate_QR
# from tools import generate_Captcha
from request_processing import signed_in


@app.route("/", methods=['GET'])
def index():
    print("1")
    resp1 = redirect(url_for('startpage'), code=302)    # Last inn denne hvis vi er innlogget
    resp2 = app.send_static_file("index.html")          # Last inn denne hvis vi ikke er innlogget
    
    try:
        return signed_in(resp1, resp2)
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet
        abort(404)  # Returner feilmelding 404

@app.route("/header.html", methods=['GET'])
def header():
    print("20")
    resp = make_response(render_template("header.html", logged_in=False))

    session_cookie = get_valid_cookie()

    if session_cookie is not None:
        cookie = Cookies.query.filter_by(session_cookie=session_cookie).first()
        user = User.query.filter_by(user_id=cookie.user_id).first()

        resp = make_response(render_template("header.html", fname=user.fname.split(' ')[0], mname=user.mname.split(' ')[0], lname=user.lname.split(' ')[0], id=user.user_id, logged_in=True, session_duration=cookie_maxAge * 1000 * 0.8, session_remaining = cookie_maxAge * 0.2 / 60))  # session_duration [ms]
    
    try:
        return resp
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet
        abort(404)  # Returner feilmelding 404

# Denne er bare for GET forespørsler.
@app.route("/login.html", methods=['GET'])
def login(page = None):
    print("2")
    resp1 = redirect(url_for('startpage'), code=302)  # Side for når en  er innlogget

    messages_1 = request.args.get('error')  # Henter argumentet error fra URL som kommer med forespørselen fra nettleseren til brukeren.
    messages_2 = request.args.get('v_mail')  # Henter argumentet error fra URL som kommer med forespørselen fra nettleseren til brukeren.
    messages_3 = request.args.get('timeout')  # Henter argumentet error fra URL som kommer med forespørselen fra nettleseren til brukeren.

    client_listing = Blacklist.query.filter_by(ip=request.remote_addr).first()

    # Side for når en ikke er innlogget
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

@app.route("/startside.html", methods=['GET'])
def startpage():
    print("3")
    resp1 = make_response()  # Ønsket side for når vi er innlogget
    resp2 = redirect(url_for('index'), code=302)  # Side for når en ikke er innlogget

    session_cookie = get_valid_cookie()
    if session_cookie is not None:
        cookie = Cookies.query.filter_by(session_cookie=session_cookie).first()
        user = User.query.filter_by(user_id=cookie.user_id).first()
        accounts = Account.query.filter_by(user_id=user.user_id).all()

        ac_name= []
        ac_nr= []
        ac_balance=[]

        transactions = set()  # Bruker set for å fjerne duplikater

        for account in accounts:
            ac_name.append(account.account_name)
            ac_nr.append(account.account_number)
            ac_balance.append(account.balance)

            for transaction in Transaction.query.filter_by(to_acc=account.account_number).all():
                transactions.add(transaction)

            for transaction in Transaction.query.filter_by(from_acc=account.account_number).all():
                transactions.add(transaction)

        transactions_list = []

        for transaction in transactions:
            transactions_list.append(transaction)

        insertion_sort_transactions(transactions_list)  # Sorterer transaksjonene, synkende rekkefølge

        transfer_time = []
        From = []
        To = []
        Msg = []
        Inn = []
        Out = []
        
        for transaction in transactions_list:
            for account in accounts:
                if transaction.to_acc == account.account_number:
                    transfer_time.append(str(datetime.strptime(transaction.transfer_time, "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d, %H:%M:%S")))
                    Msg.append(transaction.message)
                    From.append(transaction.from_acc)
                    To.append(transaction.to_acc)
                    Inn.append(transaction.amount)
                    Out.append("")
                if transaction.from_acc == account.account_number:
                    Inn.append("")
                    Out.append(transaction.amount)
                    transfer_time.append(str(datetime.strptime(transaction.transfer_time, "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d, %H:%M:%S")))
                    Msg.append(transaction.message)
                    From.append(transaction.from_acc)
                    To.append(transaction.to_acc)

        resp1 = make_response(render_template("pages/startside.html", len=len(transactions_list), transfer_time=transfer_time, From=From, To=To, Msg=Msg, Inn=Inn, Out=Out, account=accounts[0].account_number, ac_name=ac_name, ac_nr=ac_nr,ac_balance= ac_balance))

    try:
        return signed_in(resp1, resp2)
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet
        abort(404)  # Returner feilmelding 404

@app.route("/din_side.html", methods=['GET'])
def din_side():
    print("13")
    session_cookie = get_valid_cookie()

    if session_cookie is not None:
        cookie = Cookies.query.filter_by(session_cookie=session_cookie).first()
        user = User.query.filter_by(user_id=cookie.user_id).first()

        resp1 = make_response(render_template("pages/din_side.html", fname=user.fname, mname=user.mname, lname=user.lname,
                                        email=user.email, id=user.user_id, phone_num=user.phone_num,
                                        dob=user.dob, city=user.city, postcode=user.postcode, address=user.address))  # Ønsket side for når vi er innlogget
    else: 
        resp1 = make_response()  # Tom respons, denne skal ikke trigge uansett siden brukeren ikke er logget inn. Ønsket side for når vi er innlogget
    
    resp2 = redirect(url_for('index'), code=302)  # Side for når en ikke er innlogget
    
    try:
        return signed_in(resp1, resp2)
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet
        abort(404)  # Returner feilmelding 404

@app.route("/edit.html", methods=['GET'])
def edit():
    print("14")

    # Henter argumenteer fra URL som kommer med forespørselen fra nettleseren til brukeren.
    fname_error = request.args.get('fname')
    mname_error = request.args.get('mname')
    lname_error = request.args.get('lname')
    phone_num_error = request.args.get('phone_num')
    dob_error = request.args.get('dob')
    city_error = request.args.get('city')
    postcode_error = request.args.get('postcode')
    address_error = request.args.get('address')
    pswd_error = request.args.get('pswd')
    new_pswd_error = request.args.get('new_pswd')
    auth_error = request.args.get('auth')

    session_cookie = get_valid_cookie()

    if session_cookie is not None:
        cookie = Cookies.query.filter_by(session_cookie=session_cookie).first()
        user = User.query.filter_by(user_id=cookie.user_id).first()

        resp1 = make_response(render_template("pages/edit.html", fname=user.fname, mname=user.mname, lname=user.lname,
                                        email=user.email, id=user.user_id, phone_num=user.phone_num,
                                        dob=user.dob, city=user.city, postcode=user.postcode, address=user.address,
                                        fname_error=fname_error, mname_error=mname_error, lname_error=lname_error,
                                        phone_num_error=phone_num_error, dob_error=dob_error, city_error=city_error,
                                        postcode_error=postcode_error, address_error=address_error, pswd_error=pswd_error,
                                        new_pswd_error=new_pswd_error, auth_error=auth_error))  # Ønsket side for når vi er innlogget
    else:
        resp1 = make_response()  # Tom respons, denne skal ikke trigge uansett siden brukeren ikke er logget inn. Ønsket side for når vi er innlogget

    resp2 = redirect(url_for('index'), code=302)  # Side for når en ikke er innlogget
    
    try:
        return signed_in(resp1, resp2)
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet
        abort(404)  # Returner feilmelding 404

# https://stackoverflow.com/questions/49547/how-do-we-control-web-page-caching-across-all-browsers
@app.route("/registration.html", methods=['GET'])
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
    fname_error = request.args.get('fname_error')
    mname_error = request.args.get('mname_error')
    lname_error = request.args.get('lname_error')
    email_error = request.args.get('email_error')
    id_error = request.args.get('id_error')
    phone_num_error = request.args.get('phone_num_error')
    dob_error = request.args.get('dob_error')
    city_error = request.args.get('city_error')
    postcode_error = request.args.get('postcode_error')
    address_error = request.args.get('address_error')
    errors = [fname_error, mname_error, lname_error, email_error, id_error, phone_num_error, 
                dob_error, city_error, postcode_error, address_error]
    for i in errors:
        print("error" + str(errors.index(i)) + ": " + str(i))
    sitekey = '6LeVXtYZAAAAABnbl6HjUx6fqi5efMo8DJzHSucY'

    # Make_response, En alternativ måte å sende en side til brukeren, måtte gjøre det slik for å sette headers
    # trenger det ikke nå lenger siden header greiene er flyttet på, men er et greit eksempel
    resp2 = make_response(render_template("pages/registration.html", fname=fname, mname=mname, lname=lname, 
                                                                    email=email, id=uid, phone_num=phone_num, 
                                                                    dob=dob, city=city, postcode=postcode, 
                                                                    address=address, fname_error=fname_error,
                                                                    mname_error=mname_error, lname_error=lname_error,
                                                                    email_error=email_error, id_error=id_error,
                                                                    phone_num_error=phone_num_error, dob_error=dob_error,
                                                                    city_error=city_error, postcode_error=postcode_error,
                                                                    address_error=address_error, sitekey=sitekey))     

    try:
        return signed_in(resp1, resp2)
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet, i tilfellet noen prøver å skrive inn addresser til sider som ikke finnes
        abort(404)  # Returner feilmelding 404

@app.route("/transaction_view.html", methods=['GET'])
def transaction_overview(page = None):
    print("25")
    resp1 = make_response(render_template("pages/transaction_view.html", len=0))  # Side for når en er innlogget
    resp2 = redirect(url_for('index'), code=302)  # Side for når en ikke er innlogget

    # Les ut variabler
    account_number = request.args.get('cnr')
    session_cookie = get_valid_cookie()

    if session_cookie is not None and valid_account_number(account_number):
        cookie = Cookies.query.filter_by(session_cookie=session_cookie).first()
        user = User.query.filter_by(user_id=cookie.user_id).first()
        account = Account.query.filter_by(account_number=account_number).first()

        # Sjekker om dette er brukeren sin konto
        if account.user_id == user.user_id:

            transactions = Transaction.query.filter_by(to_acc=account.account_number).all() + Transaction.query.filter_by(from_acc=account.account_number).all()

            transfer_time = []
            From = []
            To = []
            Msg = []
            Inn = []
            Out = []

            insertion_sort_transactions(transactions)  # Sorterer transaksjonene, synkende rekkefølge

            for transaction in transactions:
                transfer_time.append(str(datetime.strptime(transaction.transfer_time, "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d, %H:%M:%S")))
                Msg.append(transaction.message)
                From.append(transaction.from_acc)
                To.append(transaction.to_acc)

                if transaction.to_acc == account.account_number:
                    Inn.append(transaction.amount)
                    Out.append("")

                if transaction.from_acc == account.account_number:
                    Inn.append("")
                    Out.append(transaction.amount)

            resp1 = make_response(render_template("pages/transaction_view.html", len=len(transactions), transfer_time=transfer_time, From=From, To=To, Msg=Msg, Inn=Inn, Out=Out, account=account.account_number, name=account.account_name))

    try:
        return signed_in(resp1, resp2)
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet
        abort(404)  # Returner feilmelding 404

@app.route("/verification")
def verification(style = None):
    print("9")
    verification_code = request.args.get('code')
    error = request.args.get('error')

    if contain_allowed_symbols(s=verification_code, whitelist=string.ascii_letters + string.digits):  # Kontrollerer om koden inneholder gyldige symboler før vi prøver å søke gjennom databasen med den.

        # Hent brukeren med koden i url'en, hvis det ikke er noen bruker med den koden så vil user_object = None
        user_object = User.query.filter_by(verification_code=verification_code).first()
        if user_object is not None and not user_object.verified:
            return render_template("pages/verification.html", error=error, vkey=verification_code)

    return redirect(url_for('index'), code=302)

@app.route("/password_reset_request.html")
def password_reset_request(style = None):
    sitekey = '6LeVXtYZAAAAABnbl6HjUx6fqi5efMo8DJzHSucY'
    resp1 = redirect(url_for('startpage'), code=302)  # Side for når en er innlogget
    resp2 = make_response(render_template("pages/password_reset_request.html", sitekey=sitekey))  # Side for når en ikke er innlogget

    try:
        return signed_in(resp1, resp2)
    except jinja2.exceptions.TemplateNotFound:  # Hvis siden/html filen ikke blir funnet
        abort(404)  # Returner feilmelding 404

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

@app.route("/QR.png")
def QR(style = None):
    print("35")
    vkey = request.args.get('vkey')

    if contain_allowed_symbols(s=vkey, whitelist=string.ascii_letters + string.digits):  # Kontrollerer om koden inneholder gyldige symboler før vi prøver å søke gjennom databasen med den.
        # Hent brukeren med koden i url'en, hvis det ikke er noen bruker med den koden så vil user_object = None
        user_object = User.query.filter_by(verification_code=vkey).first()
        if user_object is not None and not user_object.verified:
            _, qr = generate_QR(user_object.fname, user_object.user_id, user_object.secret_key)
            return send_file(qr, mimetype="image/png")

    abort(404)


# https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP