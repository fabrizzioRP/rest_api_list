class UserNotFound(Exception):
    pass

class UserInvalidCredentials(Exception):
    pass

class UserNotAvailable(Exception):
    pass

class ErrorDeletingUser(Exception):
    pass

class ErrorSavingUser(Exception):
    pass

class InvalidId(Exception):
    pass

class ErrorDataBase(Exception):
    pass

userError = {
    "UserNotFound": {
         "message": "Usuario no encontrado.",
         "status": 404
     },
    "UserInvalidCredentials": {
         "message": "Credenciales invalidas.",
         "status": 401
     },
    "UserNotAvailable": {
         "message": "Usuario no disponible.",
         "status": 400
     },
    "ErrorDeletingUser": {
         "message": "Error al eliminar usuario.",
         "status": 400
     },
    "ErrorSavingUser": {
         "message": "Error al guardar usuario.",
         "status": 500
     },
     "InvalidId": {
         "message": "ID invalido.",
         "status": 400
     },
    "ErrorDataBase": {
         "message": "Error inesperado en la base de datos.",
         "status": 500
     }

}

