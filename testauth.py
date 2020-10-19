# Bruk denne filen for å sjekke hva TOTP-en er til enhver tid

navn='Martin Gjerde'
from auth import generate_QR
import pyotp

secret_key, img = generate_QR(navn, 12)
print(secret_key)
totp = pyotp.TOTP(secret_key).now()
print("Current OTP:", totp)
img.show()