import pyotp
import pickle


USER_FILE_NAME = 'users.data' #database with userinformation
class User(object):
    def __init__(self, email, name='', middlename='', lastname='', userid=None, password=None, phone=None, dob=None, city='', zip='', address=''):
        self.name = name
        self.middlename = middlename
        self.lastname = lastname
        self.email = email
        self.userid = userid
        self.password = password
        self.phone = phone
        self.dob = dob
        self.city = city
        self.zip = zip
        self.address = address

        if password is None:
            self.password = pyotp.random_base32()

    def save(self):
        if len(self.email) < 13:
            return False

        users = pickle.load(open(USER_FILE_NAME, 'rb'))
        if self.email in users:
            return False
        else:
            users[self.email] = self.password
            pickle.dump(users, open(USER_FILE_NAME, 'wb'))
            return True

    def authenticate(self, otp):
        p = 0
        try:
            p = int(otp)
        except:
            return False
        t = pyotp.TOTP(self.password)
        return t.verify(p)

    @classmethod
    def get_user(cls, email):
        users = pickle.load(open(USER_FILE_NAME, 'rb'))
        if email in users:
            return User(email, users[email])
        else:
            return None
