# Bruk denne filen for å sjekke hva TOTP-en er til enhver tid

import pyotp
totp = pyotp.TOTP("FX7OI3AS7VBGDDTKMOYZ3Z6KRQ6JQF66CNCUJQAJRKGFB7Y7")
print("Current OTP:", totp.now())