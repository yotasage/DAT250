# This file is for testing different security measures

import qrcode
import pyotp
from PIL import Image, ImageDraw, ImageFont
from captcha.image import ImageCaptcha
import random
import string
import cv2
import numpy as np

def random_string_generator(size=9, chars=string.ascii_letters + string.digits):    # string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size)) 


def generate_Captcha():
    size = 20 #random.randint(10,16)
    length = 9 # random.randint(4,8)
    img = np.zeros(((size*2)+5, length*size, 3), np.uint8)
    img_pil = Image.fromarray(img+255)
    #fonts = ['arial.ttf', '']
    # Drawing text and lines
    font = ImageFont.truetype("calibri.ttf", 20) #, size=size) #truetype(random.choice(fonts), size)
    draw = ImageDraw.Draw(img_pil)
    text = ''.join(random_string_generator())
        # random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) 
        #         for _ in range(length))
    draw.text((5, 10), text, font=font, 
            fill=(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
    draw.line([(random.choice(range(length*size)), random.choice(range((size*2)+5)))
            ,(random.choice(range(length*size)), random.choice(range((size*2)+5)))]
            , width=1, fill=(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
    draw.line([(random.choice(range(length*size)), random.choice(range((size*2)+5)))
            ,(random.choice(range(length*size)), random.choice(range((size*2)+5)))]
            , width=1, fill=(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
    draw.line([(random.choice(range(length*size)), random.choice(range((size*2)+5)))
            ,(random.choice(range(length*size)), random.choice(range((size*2)+5)))]
            , width=1, fill=(random.randint(0,255), random.randint(0,255), random.randint(0,255)))

    # Adding noise and blur
    img = np.array(img_pil)
    thresh = 5/100 #random.randint(1,5)/100
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            rdn = random.random()
            if rdn < thresh:
                img[i][j] = random.randint(0,123)
            elif rdn > 1-thresh:
                img[i][j] = random.randint(123,255)
    img = cv2.blur(img,(int(size/random.randint(5,10)),int(size/random.randint(5,10))))
    img = cv2.blur(img,(int(size/random.randint(5,10)),int(size/random.randint(5,10))))
    #Displaying image
    cv2.imshow(f"{text}", img)
    cv2.waitKey()
    cv2.destroyAllWindows()

generate_Captcha()
'''
def generateCaptcha():
    length = random.randint(6,8)
    captchatext = random_string_generator(length)
    image = ImageCaptcha(str(captchatext))
    #image = ImageDraw.Draw(image)
    #qrcode.make_image(image)
    #image = image.generate_image()
    return image, captchatext

generateCaptcha()


def generate_Captcha():
    length = random.randint(6,8)
    captchatext = random_string_generator(length)
    image = ImageCaptcha()
    return image, captchatext
'''
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