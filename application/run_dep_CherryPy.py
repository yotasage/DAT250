# Denne fila kjører dere når dere vil gjøre serveren offentlig, eller generelt når dere vil teste den på en "skikkelig" server

from cheroot.wsgi import Server as WSGIServer
from cheroot.wsgi import PathInfoDispatcher as WSGIPathInfoDispatcher
from cheroot.ssl.builtin import BuiltinSSLAdapter

from app import app  # Importerer variabelen app fra filen app.py

my_app = WSGIPathInfoDispatcher({'/': app})

#                    'localhost'        privat, bare lokal
#                    '127.0.0.1'        privat, bare lokal
#                    '192.168.0.37'     offentlig, tilgjengelig for andre på nettverket (eksempel IPv4 addresse, sett inn din egen)
#                    '0.0.0.0'          offentlig, tilgjengelig for andre på nettverket (alle IP addressene til maskinen kan brukes for å nå siden)
server = WSGIServer(('0.0.0.0', 443), my_app)   # For å åpne denne serveren må en skrive https:// forran addressen

ssl_cert = "application/certificate/MyCertificate.crt"
ssl_key = "application/certificate/MyKey.key"
server.ssl_adapter =  BuiltinSSLAdapter(ssl_cert, ssl_key, None)

if __name__ == '__main__':
   try:
      server.start()
   except KeyboardInterrupt:  # Med dette så mener den ctrl+c
      server.stop()                                            # På linje 2070 i koden hvor stop() er definert har jeg satt inn: self.serving = False  # We don't care, fordi koden fryser der, er noe feil med cheroot
   except SystemExit:
      server.stop()                                            # På linje 2070 i koden hvor stop() er definert har jeg satt inn: self.serving = False  # We don't care, fordi koden fryser der, er noe feil med cheroot

# TLS test
# https://www.ssllabs.com/ssltest/index.html

# https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https
# req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# https://www.linode.com/docs/security/ssl/create-a-self-signed-tls-certificate/
# req -new -newkey rsa:4096 -x509 -sha256 -days 365 -nodes -out MyCertificate.crt -keyout MyKey.key