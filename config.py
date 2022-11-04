import os
import socket
from flask import Flask

app = Flask(__name__)

app.config['JSON_SORT_KEYS'] = False
app.config['JSON_AS_ASCII']         = False
default_datetime_format = '%Y-%m-%d %H:%M:%S'

#!Configuracion para keycloak y database
app.secret_key =""+str(os.urandom(12))

#!Configuraciones api lists

#!CONFIG SENTRY.IO
app.config['SENTRY_DSN'] = os.environ['SENTRY_DSN']
app.config['SENTRY_ENV'] = os.environ['SENTRY_ENV']
app.config['SENTRY_TRACE_RATE'] = float(os.environ['SENTRY_TRACE_RATE'])

# Configuraciones logging
app.config['LOGLEVEL'] = os.environ['LOGLEVEL']
app.config['LOGFORMAT'] = os.environ['LOGFORMAT'].format("\t", socket.gethostname())