# Bruk denne filen for å sjekke hva TOTP-en er til enhver tid

import pyotp
totp = pyotp.TOTP("YSEBRNQCNKWTEHIF")
print("Current OTP:", totp.now())