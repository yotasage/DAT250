# flask tutorial https://code.visualstudio.com/docs/python/tutorial-flask

# The command line should look something like this when the venv is activated
# windows: (.venv_win) PS E:\...\DAT250\Prosjekt\DAT250> 
# mac: (.venv_mac) PS E:\...\DAT250\Prosjekt\DAT250> 

# To run the server in vs code, type the following command in the terminal after activating the venv:
# windows: python -m flask run
# mac: python3 -m flask run

# server options:
# these are safe:
#   python -m flask run
#   flask run
# this one will make the server available to everyone on your network. This is an unsafe option as anyone could run arbitrary code on your pc when you run the server in this way:
# flask run --host 0.0.0.0

# The development server looks for app.py by default. 

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