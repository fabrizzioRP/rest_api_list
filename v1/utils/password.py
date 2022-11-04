import secrets
import string
import base64
from werkzeug.security import generate_password_hash

def create_password():
    # Se crea la contraseña automaticamente.
    alphabet = string.ascii_letters + string.digits + "!@#$*"
    password = ''.join(secrets.choice(alphabet) for i in range(12))
    return password, generate_password_hash(password)

def encoding_password(password):
    pass_bytes = password.encode('ascii')
    base64_bytes = base64.b64encode(pass_bytes)
    base64_pass = base64_bytes.decode('ascii')
    return base64_pass

def decoder_password(password):
    base64_bytes = password.encode('ascii')
    pass_bytes = base64.b64decode(base64_bytes)
    password = pass_bytes.decode('ascii')
    return password