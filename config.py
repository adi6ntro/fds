import os
import json

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = 'top-secret!'
    with open("config.json") as json_data_file:
        data = json.load(json_data_file)
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     'mysql+pymysql://root:@localhost:3306/dbfds'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://'+data['db_username']+':'+data['db_password']+'@'+data['db_host']+':'+data['db_port']+'/'+data['db_name']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['adi.guntoro@ottodigital.id']
    POSTS_PER_PAGE = 10
    # MAIL_DEFAULT_SENDER = 'support@ottofds.id'
