import smtplib, ssl, configparser, sys, os
from mongoengine import connect
from local_config import mongo_config, secret_key
import logging


def settings():
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    CONFIG_FILE = os.path.join(BASE_PATH, 'config.ini')
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    entity_config = config['EMAIL']

    result = dict()
    database = dict()
    email = dict()

    # database['db'] = mongo_config.get('MONGODB_DB', 'email')
    # database['user'] = mongo_config.get('MONGODB_USERNAME', None)
    # database['pass'] = mongo_config.get('MONGODB_PASSWORD', None)
    # database['host'] = mongo_config.get('MONGODB_HOST', '127.0.0.1')
    # database['port'] = mongo_config.get('MONGODB_PORT', 27017)
    # database['authsource'] = mongo_config.get('MONGODB_AUTHSOURCE', None)
    # database['authmechanism'] = mongo_config.get('MONGODB_AUTHMECHANISM', None)
    # database['host_string'] = 'mongodb://%s/%s?authSource=%s' % (database['host'], database['db'], database['authsource'] )

    # database['link'] = connect(
    #     db=database['db'],
    #     username=database['user'], 
    #     password=database['pass'],
    #     host=database['host'],
    #     port=int(database['port']),
    #     authentication_source=database['authsource'],
    #     connect=False
    #     )

    email['server'] = entity_config.get('EMAIL_SERVER')
    email['port'] = entity_config.get('EMAIL_PORT')
    email['sender'] = entity_config.get('EMAIL_SENDER')
    email['passwd'] = entity_config.get('EMAIL_PASSWD')
    email['recept'] = entity_config.get('EMAIL_RECEPT')

    result['database'] = mongo_config
    result['email'] = email
    logging.info("Result database: {}".format(result['database']))
    logging.info("Result email: {}".format(result['email']))

    return result


    
