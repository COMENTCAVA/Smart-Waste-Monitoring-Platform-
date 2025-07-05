import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///wdp.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LANGUAGES = ['fr', 'en', 'de']
    BABEL_DEFAULT_LOCALE = 'fr'
    BABEL_DEFAULT_TIMEZONE = 'UTC'

