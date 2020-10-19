import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

############################################################################################
#
#
#   Et eksempelscript på kryptering av databaser.
#
#
############################################################################################

secret_key = 'secretkey1234'
# setup
engine = create_engine('sqlite:///etc/test_database.db')
connection = engine.connect()
Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(EncryptedType(sa.Unicode,
                                        secret_key,
                                        AesEngine,
                                        'pkcs5'))
    access_token = sa.Column(EncryptedType(sa.String,
                                            secret_key,
                                            AesEngine,
                                            'pkcs5'))
    is_active = sa.Column(EncryptedType(sa.Boolean,
                                        secret_key,
                                        AesEngine,
                                        'zeroes'))
    number_of_accounts = sa.Column(EncryptedType(sa.Integer,
                                                    secret_key,
                                                    AesEngine,
                                                    'oneandzeroes'))


sa.orm.configure_mappers()
Base.metadata.create_all(connection)

# create a configured "Session" class
Session = sessionmaker(bind=connection)

# create a Session
session = Session()

# example
user_name = u'secret_user'
test_token = 'atesttoken'
active = True
num_of_accounts = 2

user = User(username=user_name, access_token=test_token,
            is_active=active, number_of_accounts=num_of_accounts)
session.add(user)
session.commit()

user_id = user.id

session.expunge_all()

user_instance = session.query(User).get(user_id)

print('id: {}'.format(user_instance.id))
print('username: {}'.format(user_instance.username))
print('token: {}'.format(user_instance.access_token))
print('active: {}'.format(user_instance.is_active))
print('accounts: {}'.format(user_instance.number_of_accounts))

# teardown
# session.close_all()
# Base.metadata.drop_all(connection)
# connection.close()
# engine.dispose()