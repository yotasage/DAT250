from flask import redirect, url_for

from app import app
from tools import update_cookie_clientside, get_valid_cookie
from tasks import delete_cookie

# Denne er bare for GET forespørsler.
@app.route("/<data>", methods=['GET'])  # https://flask.palletsprojects.com/en/1.1.x/quickstart/
def get_data(data = None):
    print("get_handlers - 1")

    # Denne kjøres når logg ut knappen trykkes på
    if data == "logout":
        session_cookie = get_valid_cookie()  # Henter gyldig cookie fra headeren hvis det er en

        # Om vi fikk en gyldig header, med en gyldig cookie, da er vi faktisk logget inn, og kan derfor logge ut brukeren.
        if session_cookie is not None:
            resp = redirect(url_for('login'), code=302)
            delete_cookie(session_cookie)
            update_cookie_clientside(session_cookie, resp, 0)
            return resp


    return redirect(url_for('index'), code=302)