# Bruk denne filen for å sjekke hva TOTP-en er til enhver tid

import pyotp
totp = pyotp.TOTP("6ZIU4RBAIEQGCF27BGSIHMQBOAVMK2IN")
print("Current OTP:", totp.now())