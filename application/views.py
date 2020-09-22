# The views are the handlers that respond to requests from web browsers or other clients. 
# In Flask handlers are written as Python functions. 
# Each view function is mapped to one or more request URLs.

import datetime
from flask import render_template

from app import app # Importerer Flask objektet app
from tools import send_mail

@app.route("/")
@app.route('/index')
def hello_there():
    print("home")
    return render_template("index.html", date=datetime.datetime.now(), username="Vebjørn")

@app.route("/mail")
def send_mails():
    send_mail()
    return render_template("index.html", date=datetime.datetime.now())

@app.route("/favicon.ico")
def fav():
    print("fav")
    return app.send_static_file("assets/favicon.ico")

@app.route("/pages/<page>")
def pages(page = None):
    print(f"page = {page}")
    return render_template("pages/" + page, date=datetime.datetime.now())

@app.route("/assets/<asset>")
def assets(asset = None):
    print(f"asset = {asset}")
    return app.send_static_file("assets/" + asset)

@app.route("/styles/<asset>")
def styles(style = None):
    print(f"style = {style}")
    return app.send_static_file("style/" + style)