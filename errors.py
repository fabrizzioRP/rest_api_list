import json
from v1.errors.main import *

class InternalServerError(Exception):
    pass

class SchemaValidationError(Exception):
    pass

class UnauthorizedError(Exception):
    pass

class ExpiredSignatureError(Exception):
    pass

class InvalidSignatureError(Exception):
    pass

class SignatureError(Exception):
    pass

CUSTOM_ERRORS = {
    "InternalServerError": {
        "message": "Error interno del servidor.",
        "status": 500
    },
     "SchemaValidationError": {
         "message": "Faltan campos obligatorios.",
         "status": 400
     },
     "UnauthorizedError": {
         "message": "Usuario o contraseña invalidos.",
         "status": 401
     },
     "ExpiredSignatureError": {
         "message": "Token Expirado.",
         "status": 401
     },
     "InvalidSignatureError": {
         "message": "Token invalido.",
         "status": 401
     },
     "SignatureError": {
         "message": "Error con el token ingresado.",
         "status": 401
     },
}

CUSTOM_ERRORS.update(userError)
CUSTOM_ERRORS.update(sttError)
