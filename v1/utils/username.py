import secrets
import string
import base64
from db import Mongo

def create_username(id_cliente, username):
    # Se crea la contraseña automaticamente.
    alphabet = string.digits
    try:
        collecction = Mongo('clientes').collection
        client = collecction.find_one({"id_cliente": id_cliente})
    except Exception as error:
        raise error

    ext = ''.join(secrets.choice(alphabet) for i in range(0,4))
    new_username = username + "." + ext

    count = 0


    while new_username in client['usuarios']:
        if count > 1000:
            return False, "Error al crear usuario."

        ext = ''.join(secrets.choice(alphabet) for i in range(0,4))
        new_username = username + "." + ext
        count += 1

    return True, new_username
