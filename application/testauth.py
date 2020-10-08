# Bruk denne filen for å sjekke hva TOTP-en er til enhver tid
navn='Martin'
from auth import generate_QR
generate_QR(navn, 12)
import pyotp
totp = pyotp.TOTP(generate_QR.secret_key)
print("Current OTP:", totp.now())