# Denne fila kjører dere når dere vil teste serveren, denne burde ikke brukes for å gjøre serveren offentlig.

from app import app  # Importerer variabelen app fra filen app.py

#       host='localhost'        privat, bare lokal
#       host='127.0.0.1'        privat, bare lokal
#       host='192.168.0.37'     offentlig, tilgjengelig for andre på nettverket (eksempel IPv4 addresse, sett inn din egen)
#       host='0.0.0.0'          offentlig, tilgjengelig for andre på nettverket (alle IP addressene til maskinen kan brukes for å nå siden)
app.run(host='localhost', debug=True)  # Runs the server in development mode using the integrated server in Flask