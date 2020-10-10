import qrcode
import pyotp
from PIL import Image
from captcha.image import ImageCaptcha
import random
import string

def random_string_generator(size=6, chars=string.ascii_letters + string.digits):    # string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size)) 

def generateCaptcha():
    length = random.randint(6,8)
    captchatext = random_string_generator(length)
    image = ImageCaptcha(str(captchatext))
    image = image.generate_image()
    return image, captchatext




def generate_Captcha():
    length = random.randint(6,8)
    captchatext = random_string_generator(length)
    image = ImageCaptcha()
    return image, captchatext
'''
def generate_QR(fname, id):
    secret_key = pyotp.random_base32(length=32) # Using 256 bits secret key, see source below
    secret_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(name=(str(fname) + ' (' + str(id) + ')'), issuer_name='JAMVP Bank')
    qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
    )
    qr.add_data(secret_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    width, height = img.size
    logo_size = 80
    logo = Image.open('application/static/assets/logo_no_white.png')
    xmin = ymin = int((width / 2) - (logo_size / 2))
    xmax = ymax = int((width / 2) + (logo_size / 2))
    logo = logo.resize((xmax - xmin, ymax - ymin))
    img.paste(logo, (xmin, ymin, xmax, ymax))
    return secret_key, img

# https://www.cryptomathic.com/news-events/blog/classification-of-cryptographic-keys-functions-and-properties


# Hente inn secret_key fra databasen hos brukeren, sette inn id til brukeren, både userid og fornavn

'''




'''
Kilder:

https://sahandsaba.com/two-step-verification-using-python-pyotp-qrcode-flask-and-heroku.html
https://github.com/sahands/python-totp
https://github.com/pyauth/pyotp
https://github.com/neocotic/qrious
https://github.com/pyauth/pyotp
https://github.com/tadeck/onetimepass
https://stackoverflow.com/questions/8529265/google-authenticator-implementation-in-python
https://stackoverflow.com/questions/45481990/how-to-insert-logo-in-the-center-of-qrcode-in-python


'''