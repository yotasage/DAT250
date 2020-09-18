# Denne fila kjører dere når dere vil gjøre serveren offentlig, eller generelt når dere vil teste den på en "skikkelig" server

import waitress

from app import app  # Importerer variabelen app fra filen app.py

#                   host='localhost'        privat, bare lokal
#                   host='127.0.0.1'        privat, bare lokal
#                   host='192.168.0.37'     offentlig, tilgjengelig for andre på nettverket (eksempel IPv4 addresse, sett inn din egen)
#                   host='0.0.0.0'          offentlig, tilgjengelig for andre på nettverket (alle IP addressene til maskinen kan brukes for å nå siden)
waitress.serve(app, host='0.0.0.0', port=8080, threads=4) # Runs the server in "deployment" mode using waitress as a server. This is safer than the integrated server in Flask