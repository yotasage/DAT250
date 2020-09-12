# flask tutorial https://code.visualstudio.com/docs/python/tutorial-flask

# imports
import datetime
from flask import Flask
from flask import render_template
from flask import app

# something
app = Flask(__name__)

@app.route("/")
def hello_there():
    print("home")
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