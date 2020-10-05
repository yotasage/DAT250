# Denne fila kjører dere når dere vil teste serveren, denne burde ikke brukes for å gjøre serveren offentlig.

from app import app  # Importerer variabelen app fra filen app.py

ssl_cert = "application/certificate/MyCertificate.crt"
ssl_key = "application/certificate/MyKey.key"

#       host='localhost'        privat, bare lokal
#       host='127.0.0.1'        privat, bare lokal
#       host='192.168.0.37'     offentlig, tilgjengelig for andre på nettverket (eksempel IPv4 addresse, sett inn din egen)
#       host='0.0.0.0'          offentlig, tilgjengelig for andre på nettverket (alle IP addressene til maskinen kan brukes for å nå siden)
app.run(host='0.0.0.0', port=443, debug=True, ssl_context=(ssl_cert, ssl_key))  # Runs the server in development mode using the integrated server in Flask
# app.run(host='0.0.0.0', port=80, debug=True)  # Runs the server in development mode using the integrated server in Flask

# https://certbot.eff.org/lets-encrypt/windows-other