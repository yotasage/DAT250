from app import db
from flask_sqlalchemy import SQLAlchemy


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    fname = db.Column(db.String, unique=False, nullable=False)
    mname = db.Column(db.String, unique=False, nullable=True)
    lname = db.Column(db.String, unique=False, nullable=False)
    phone_num = db.Column(db.Integer, unique=True, nullable=False)
    dob = db.Column(db.String, unique=False, nullable=False)
    city = db.Column(db.String, unique=False, nullable=False)
    postcode = db.Column(db.Integer, unique=False, nullable=False)
    address = db.Column(db.String, unique=False, nullable=False)
    hashed_password = db.Column(db.String, unique=False, nullable=True)
    salt = db.Column(db.String, unique=False, nullable=True)
    verification_code = db.Column(db.String, unique=True, nullable=True)
    verified = db.Column(db.Boolean, unique=False, nullable=False)
    password_reset_code = db.Column(db.String, unique=True, nullable=True)
    secret_key = db.Column(db.String, unique=True, nullable=False)
    failed_logins = db.Column(db.Integer, unique=False, nullable=False)
    blocked_login_until = db.Column(db.String, unique=False, nullable=True)


class Blacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String, unique=True, nullable=False)
    last = db.Column(db.String, unique=False, nullable=False)                        # Sist gang en request ble gjort
    # start = db.Column(db.String, unique=False, nullable=False)                       # Når det begynte å bli for mange requests
    frequent_request_count = db.Column(db.Integer, unique=False, nullable=False)     # Hvor mange ganger brukeren har sent for hyppige requests
    wrong_password_count = db.Column(db.Integer, unique=False, nullable=False)       # Hvor mange ganger brukeren har skrevet inn feil passord
    blocked_until = db.Column(db.String, unique=False, nullable=True)
    blocked_login_until = db.Column(db.String, unique=False, nullable=True)
    reason = db.Column(db.String, unique=False, nullable=True)                      


class Cookies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=False, nullable=False)
    session_cookie = db.Column(db.String, unique=True, nullable=False)
    valid_to = db.Column(db.String, unique=False, nullable=False)


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=False, nullable=False)
    balance = db.Column(db.Integer, unique=False, nullable=False)
    account_number = db.Column(db.String, unique=True, nullable=False)
    account_name = db.Column(db.String, unique=False, nullable=False)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transfer_time = db.Column(db.String, unique=False, nullable=False)
    from_acc = db.Column(db.String, unique=False, nullable=False)
    to_acc = db.Column(db.String, unique=False, nullable=False)
    message = db.Column(db.String, unique=False, nullable=False)
    amount = db.Column(db.Integer, unique=False, nullable=False)
