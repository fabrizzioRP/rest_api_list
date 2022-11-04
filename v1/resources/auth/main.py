import json
import logging
from flask import Flask, g,request,session
import requests
from authorization import Auth #Se importa el decorador
from dbDecorator import  dbAccess #Se importa el decorador
from mongoengine import *
from flask import Flask,session


import logging
app = Flask(__name__)
app.secret_key = 'super secret key'

AuthConfig = {
    "ClientID":str(os.environ["KEYCLOAK_CLIENTID"]), #cliente que utilizara la aplicacion (cliente a nivel keycloak)
    "ClientSecret":str(os.environ["KEYCLOAK_CLIENTSECRET"]),
    "UrlToken":str(os.environ["KEYCLOAK_URLTOKEN"]), #endpoint para obtener token
    "UrlInfo":str(os.environ["KEYCLOAK_URLINFO"]) #endpoint para obtener informacion de usuario
    }
DbConfig = {"host":str(os.environ["BD_HOST"]), #ip de la base de datos principal de xentric
    "port":str(os.environ["BD_PORT"]), #puerto de la base de datos principal de xentric
    "user":str(os.environ["BD_USER"]), #usuario de la base de datos principal de xentric
    "pass":str(os.environ["BD_PASS"]),#contraseña de la base de datos principal de xentric
    "EncriptWord": str(os.environ["ENCRIPTWORD"]) #palabra clave para encriptacion y desencriptacion
    }
app.config['AuthConfig']=AuthConfig
app.config['DbConfig']=DbConfig

@app.route('/list', methods=['GET'])
@Auth.authenticate #se pone el decorador arriba del metodo del endpoint que se desea asegurar
@dbAccess.mongoEngineAccess #decorador de bd
def engine():
    userdata=session["user"]
    post = Post(title="Quora rocks", author="Ross", tags=['tutorial', 'how-to'])
    post.save()
    session.clear() #limpiado de sesion
    return json.dumps({'resp': "Soy un endpoint seguro","user":userdata})


@app.route('/list2', methods=['GET'])
@Auth.authenticate #se pone el decorador arriba del metodo del endpoint que se desea asegurar
@dbAccess.pymongoAccess #decorador de base de datos
def pymongo():
    userdata=session["user"]
    session.clear() #se limpia la sesion
    return json.dumps({'resp': "Soy un endpoint seguro","user":userdata})










class Post(Document):
        title = StringField(max_length=120, required=True)
        author = StringField(required=True)
        tags = ListField(StringField(max_length=30))






app.run()




