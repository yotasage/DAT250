# flask tutorial https://code.visualstudio.com/docs/python/tutorial-flask
# The development server looks for app.py by default. 

import datetime
from flask import Flask
from flask import render_template
from flask import app
app = Flask(__name__)

# @app.route("/")
# def home():
#     return "Hello, Flask!"

@app.route("/")
def hello_there():
    return render_template("index.html", date=datetime.datetime.now())

@app.route("/pages/<page>")
def pages(page = None):
    print(page)
    return render_template("/assets/" + page, date=datetime.datetime.now())

@app.route("/assets/<asset>")
def assets(asset = None):
    print(asset)
    return app.send_static_file("/assets/" + asset)

@app.route("/styles/<asset>")
def styles(asset = None):
    print(asset)
    return app.send_static_file("/styles/" + asset)