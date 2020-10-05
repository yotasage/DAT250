from app import app, db
from flask_sqlalchemy import SQLAlchemy
from models import Cookies

def delete_cookie(cookie_in_question):
    cookie = Cookies.query.filter_by(session_cookie=cookie_in_question).first()
    db.session.delete(cookie)
    db.session.commit()
