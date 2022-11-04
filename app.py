from flask_restful import Api
from flask_cors import CORS
from errors import CUSTOM_ERRORS
from config import app
from v1.resources.routes import initialize_routes
import logging

# Sentry Import
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Logging set-up
logger = logging.getLogger(__name__)
logging.basicConfig(format=app.config.get('LOGFORMAT'), level=app.config.get('LOGLEVEL','WARNING'))

sentry_sdk.init(
    dsn=app.config['SENTRY_DSN'],
    integrations=[FlaskIntegration()],
    environment=app.config['SENTRY_ENV'],
    debug=False,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=app.config['SENTRY_TRACE_RATE']
)

# Flask restful con errores personalizados
CORS(app)
api = Api(app, errors=CUSTOM_ERRORS)

# Importando las rutas (endpoints)
initialize_routes(api)
#logger.warning("RUNNING API")

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5050, debug=True)
