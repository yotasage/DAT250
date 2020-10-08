# Bruk denne filen for å sjekke hva TOTP-en er til enhver tid

navn='Martin Gjerde'
from auth import generate_QR
secret_key = generate_QR(navn, 12)
import pyotp
print(secret_key)
totp = pyotp.TOTP(secret_key)
print("Current OTP:", totp.now())
generate_QR.img.show()