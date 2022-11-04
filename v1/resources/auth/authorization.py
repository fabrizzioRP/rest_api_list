from functools import wraps
from flask import request, g,session
import requests
import json
import os
from config import app
class Auth():
    if("AuthConfig" not in app.config):
        AuthConfig={"ClientID":str(os.environ["KEYCLOAK_CLIENTID"]), #cliente que utilizara la aplicacion (cliente a nivel keycloak)
                    "ClientSecret":str(os.environ["KEYCLOAK_CLIENTSECRET"]),
                    "UrlToken":str(os.environ["KEYCLOAK_URLTOKEN"]), #endpoint para obtener token
                    "UrlInfo":str(os.environ["KEYCLOAK_URLINFO"]) #endpoint para obtener informacion de usuario
        }
        DbConfig={"host":str(os.environ["BD_HOST"]), #ip de la base de datos principal de xentric
                "port":str(os.environ["BD_PORT"]), #puerto de la base de datos principal de xentric
                "user":str(os.environ["BD_USER"]), #usuario de la base de datos principal de xentric
                "pass":str(os.environ["BD_PASS"]),#contraseña de la base de datos principal de xentric
                "EncriptWord": str(os.environ["ENCRIPTWORD"]) #palabra clave para encriptacion y desencriptacion
                }
        app.config['AuthConfig']=AuthConfig
        app.config['DbConfig']=DbConfig


    AuthConfig=app.config["AuthConfig"]
    path=os.path.dirname(os.path.realpath(__file__))
    
    config=AuthConfig
    url = config["UrlInfo"]
    with open(path+'/scopes.json') as file:
        scopes = json.load(file)
    def authenticate(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            rule = request.endpoint
            authprocess = Auth()
            method=request.method.upper()
            scope=authprocess.scopes[method]
            #obtenemos el nombre del recurso a utilizar desde la url
            if("auth:" in rule):
                if(rule.count(":")==1):
                    resource=rule.replace("auth:","")
                elif(rule.count(":")==2):
                    primero=rule.index(":")
                    segundo=rule.index(":", primero + 1)
                    resource=rule[primero+1:segundo]
                    

            else:
                resource=str(request.url_rule)
                if(resource.startswith("/")):
                    resource=resource[1:]
                resource=resource.split('/')
                resource=resource[0]
            #se obtienen las credenciales de keycloak desde el archivo de configuracion
            grant_type = "password"
            ClientID = authprocess.config["ClientID"]
            ClientSecret = authprocess.config["ClientSecret"]
            
            if (request.authorization is not None): #en el caso de obtener autentificacion basica de parte del usuario se obtiene el token
                username = request.authorization.username
                password = request.authorization.password
                res=authprocess.getToken(username, password,grant_type, ClientID, ClientSecret)
                if res!=True:
                    return res
               # print("token completo: "+str(g.auth_data))
                token=g.auth_data["access_token"]

            elif "Authorization" in request.headers: #en el caso de obtener el token directamente del usuario se elimina el "Bearer" y se almacena en una variable
                token=request.headers["Authorization"] #se obtiene el token desde el header
                if(token.startswith("Bearer ")):
                    token=token.replace("Bearer ","")
            
            elif ("username" in request.args and "password" in request.args):
                username=request.args["username"]
                password=request.args["password"]
                res=authprocess.getToken(username, password,grant_type, ClientID, ClientSecret)
                if res!=True:
                    return res
               # print("token completo: "+str(g.auth_data))
                token=g.auth_data["access_token"]
            else: #en el caso de no existir un toquen ni una autentificacion basica se envia un mensaje indicando que el usuario no tiene permiso
                response ={'message':'unauthorized'}
                return response, 401
            session["token"]=token
            res=authprocess.getAcces(token,ClientID,resource,scope) #se verifica el acceso del usuario al recurso  
            if(res==True): #en el caso de tener permiso se obtiene obtiene la informacion del usuario
                res=authprocess.getInfo(token) #se obtiene la informacion del usuario
                if res!=True:
                    return res
                    #   print("token: "+str(token))
                res = f(*args, **kwargs)                               # Se ejecuta la funcion del endpoint requerido.
                return res                                             # Retorna el valor de la funcion.
            
            else:
                return res
        return wrapper


    def getToken(self,username,password,grant_type,ClientID,ClientSecret): #metodo para obtener el token 
        try:
            authprocess=Auth()
            url = authprocess.config["UrlToken"]
            payload= 'username={0}&password={1}&grant_type={2}&client_id={3}&client_secret={4}'.format(username, password, grant_type, ClientID, ClientSecret)
            #payload='username=usertest&password=123&grant_type=password&ClientID=flask_api&ClientSecret=73cb0ae6-48a1-464c-a17d-134ae1503953'
            headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            res = response.json()
            if response.status_code == 200:
                # print(res)
                g.auth_data = res
                return True
            else:
                return res
        except:
            return False
            
    def getInfo(self,token):#metodo para obtener informacion
        authprocess=Auth()    
        url = authprocess.config["UrlInfo"]
        payload={}
        headers = {
        'Authorization': 'Bearer '+str(token)
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        if(response.status_code == 200):
            data=response.json()
            #print(data)
            session["user"]=data
            return True
        else:
            return response.json()
    

    def getAcces(self,token,ClientID,resource,scope): #metodo para verificar el acceso del usuario a un recurso
        authprocess=Auth()   
        url = authprocess.config["UrlToken"]
        payload='grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Auma-ticket&audience='+ClientID+'&permission='+resource+"&scope="+scope
        headers = {
        'Authorization': 'Bearer '+str(token),
        'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        if(response.status_code == 200):
            return True
        else:
            return response.json()
