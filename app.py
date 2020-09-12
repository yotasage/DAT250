# flask tutorial https://code.visualstudio.com/docs/python/tutorial-flask

# To activate the virtual environment (venv) type in the following command in the terminal:
# windows: & "e:/.../DAT250/Prosjekt/DAT250/.venv_win/Scripts/Activate.ps1"
# mac: & "e:/.../DAT250/Prosjekt/DAT250/.venv_mac/Scripts/Activate.ps1"

# The command line should look something like this when the venv is activated
# windows: (.venv_win) PS E:\...\DAT250\Prosjekt\DAT250> 
# mac: (.venv_mac) PS E:\...\DAT250\Prosjekt\DAT250> 

# To run the server in vs code, type the following command in the terminal after activating the venv:
# windows: python -m flask run
# mac: python3 -m flask run

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