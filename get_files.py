import jinja2  # For å kunne håndtere feil som 404
from flask import render_template, request, redirect, url_for, abort, make_response

from app import app

@app.route("/<asset>.png")
def assets(asset = None):
    print("get_files - 1")
    return app.send_static_file("assets/" + asset + ".png")

# Må teste om denne gjør noe
@app.route("/favicon.ico")
def favicon():
    print("get_files - 2")
    return app.send_static_file("favicon.png")

@app.route("/<style>.css")
def styles(style = None):
    print("get_files - 3")
    return app.send_static_file("styles/" + style + ".css")
