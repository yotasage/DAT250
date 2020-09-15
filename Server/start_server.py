import waitress

from app import *

waitress.serve(app, host='localhost', port=8080, threads=1) #WAITRESS!