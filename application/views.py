# The views are the handlers that respond to requests from web browsers or other clients. 
# In Flask handlers are written as Python functions. 
# Each view function is mapped to one or more request URLs.

import datetime
from flask import render_template, request

from app import app # Importerer Flask objektet app
from tools import send_mail

@app.route("/")
@app.route('/index')
def index():
    return render_template("index.html", date=datetime.datetime.now(), username="Vebjørn")

@app.route("/pages/login.html", methods=['GET'])
def login(page = None):
    messages = request.args.get('error')
    return render_template("pages/login.html", date=datetime.datetime.now(), error=messages)

@app.route("/pages/<page>", methods=['GET'])
def pages(page = None):
    return render_template("pages/" + page, date=datetime.datetime.now(), error=None)

@app.route("/assets/<asset>")
def assets(asset = None):
    return app.send_static_file("assets/" + asset)

@app.route("/styles/<asset>")
def styles(style = None):
    return app.send_static_file("style/" + style)