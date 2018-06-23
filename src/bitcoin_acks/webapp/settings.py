import os
import random
import string

from bitcoin_acks.database.session import get_url


def generate_secret():
    alphanumeric = string.ascii_uppercase + string.ascii_lowercase + string.digits
    x = ''.join(random.choice(alphanumeric) for _ in range(32))
    return x


class Config(object):
    DEBUG = False
    FLASK_ADMIN_FLUID_LAYOUT = True
    SECRET_KEY = os.environ.get('SECRET_KEY', default=generate_secret())
    SQLALCHEMY_DATABASE_URI = get_url()
