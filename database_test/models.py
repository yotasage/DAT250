from app import db
from flask_sqlalchemy import SQLAlchemy


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    balance = db.Column(db.Integer, unique=True, nullable=False)
    account_number = db.Column(db.String, unique=True, nullable=False)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    date = db.Column(db.String, unique=True, nullable=False)
    time = db.Column(db.Integer, unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


        