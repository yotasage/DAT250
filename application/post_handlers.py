import datetime
from flask import render_template, request, redirect, url_for 

from app import app # Importerer Flask objektet app
from tools import send_mail

username = "admin"
password = "pass"

@app.route("/pages/<page>", methods=['POST'])  # https://flask.palletsprojects.com/en/1.1.x/quickstart/
def post_data(page = None):
    if page == "login_data":
        if (request.form.get("uname") == username) & (request.form.get("pswd") == password):
            return redirect("startside.html", code=302)

        return redirect(url_for('login', error="True"), code=302)
    return redirect(url_for('index'), code=302)


# https://tedboy.github.io/flask/generated/generated/werkzeug.ImmutableMultiDict.html
# https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request
# request.form