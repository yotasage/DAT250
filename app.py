# flask tutorial https://code.visualstudio.com/docs/python/tutorial-flask
# The development server looks for app.py by default. 

from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Flask!"