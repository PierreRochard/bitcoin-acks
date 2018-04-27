import os


class Config(object):
    DEBUG = False
    FLASK_ADMIN_FLUID_LAYOUT = True
    SECRET_KEY = os.environ['SECRET_KEY']
