from functools import wraps
from flask import request, g,session
import requests
import json
from pymongo import MongoClient
from functools import wraps
from secrets import choice
from string import ascii_letters, ascii_uppercase, digits
from datetime import datetime
from mongoengine import connect,register_connection
from mongoengine import *
import threading
from v1.resources.auth.encript import decrypt
import os
from mongoengine.connection import disconnect
from config import app
import logging

path=os.path.dirname(os.path.realpath(__file__))

DbConfig=app.config["DbConfig"]
config=DbConfig
username=config["user"]
password=config["pass"]
EncriptWord=config["EncriptWord"]
host=str(config["host"]+":"+config["port"])
myclient =  MongoClient('mongodb://%s:%s@%s' % (username, password,host))
class dbAccess():
    def mongoEngineAccess(f):  
        @wraps(f)
        def wrapper(*args, **kwargs):
            user=session["user"]
            group=str(user["bdName"])
            mydb = myclient["xentric_db"]
            mycol = mydb["clients"]
            
            d=mycol.find_one({"client": group})
            

            if d is None:
                logging.info("creando base de datos")
                dbUser=user["bdUser"]
                data={"client":group,"user":dbUser,"bdName":group}
                mycol.insert_one(data)
                userName=""
                userLastname=""
                email=""
                if "given_name" in user:
                    userName=user["given_name"]
                if "family_name" in user:
                    userLastname=user["family_name"]
                if "email" in user:
                    email=user["email"]            
                mycol = mydb["user"]
                permissions=getPermission(session["token"])
                
                data={"client":group,"user":user["preferred_username"],"name":userName,"last_name":userLastname,"email":email,"permission":permissions}
                mycol.insert_one(data)
                pw=decrypt(user["bdPass"],EncriptWord)
                try:
                    mydb = myclient[group]
                    mycol = mydb["info"]
                    data2={"client":group,"creation_date":datetime.now(),"created_by":user["preferred_username"]}
                    mycol.insert_one(data2)
                    mydb.add_user(dbUser,pw)
                    resp=connectMongoEngine(host,group,dbUser,pw)
                    session["dbMongoEngine"]=resp
                except Exception as ex:
                    logging.critical("error: "+str(ex))
            else:
               
                dbUser=user["bdUser"]
                pw=decrypt(user["bdPass"],EncriptWord)
                resp=connectMongoEngine(host,group,dbUser,pw)
                user=session["user"]
                session["dbMongoEngine"]=resp
                user=session["user"]
                x = threading.Thread(target=addUser, args=(user,session["token"],))
                x.start()
                rule=request.endpoint
                if("auth:" in rule):
                    resource=rule.replace("auth:","")
                else:
                    resource=str(request.url_rule)
                    if(resource.startswith("/")):
                        resource=resource[1:]
                    resource=resource.split('/')
                    resource=resource[0]
                ip_address = request.remote_addr
                x = threading.Thread(target=addRegister, args=(user,resource,ip_address,))
                x.start()
            res = f(*args, **kwargs)
            session.clear()                                                   # Se ejecuta la funcion del endpoint requerido.
            return res                                             # Retorna el valor de la funcion.
        
        return wrapper



    def pymongoAccess(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user=session["user"]
            group=str(user["bdName"])
            mydb = myclient["xentric_db"]
            mycol = mydb["clients"]
            try: 
                d=mycol.find_one({"client": group})
            except Exception as ex:
                logging.critical("error"+str(ex))
            if d is None:
                dbUser=user["bdUser"]
                data={"client":group,"user":dbUser,"bdName":group}
                mycol.insert_one(data)
                userName=""
                userLastname=""
                email=""
                if "given_name" in user:
                    userName=user["given_name"]
                if "family_name" in user:
                    userLastname=user["family_name"]
                if "email" in user:
                    email=user["email"]            
                mycol = mydb["user"]
                permissions=getPermission(session["token"])
                data={"client":group,"user":user["preferred_username"],"name":userName,"last_name":userLastname,"email":email,"permission":permissions}
                mycol.insert_one(data)
                pw=decrypt(user["bdPass"],EncriptWord)
                mydb = myclient[group]
                mycol = mydb["info"]
                data2={"client":group,"creation_date":datetime.now(),"created_by":user["preferred_username"]}
                mycol.insert_one(data2)
                mydb.add_user(dbUser,pw)
                resp=connectPyMongo(host,group,dbUser,pw)
                session["dbPyMongo"]=resp
            else:
                dbUser=user["bdUser"]
                pw=decrypt(user["bdPass"],EncriptWord)
                resp=connectPyMongo(host,group,dbUser,pw)
                user=session["user"]
                session["dbPyMongo"]=resp
                user=session["user"]
                x = threading.Thread(target=addUser, args=(user,session["token"],))
                x.start()
                rule = request.endpoint
                if("auth:" in rule):
                    resource=rule.replace("auth:","")
                else:
                    resource=str(request.url_rule)
                    if(resource.startswith("/")):
                        resource=resource[1:]
                    resource=resource.split('/')
                    resource=resource[0]
                ip_address = request.remote_addr
                x = threading.Thread(target=addRegister, args=(user,resource,ip_address,))
                x.start()

        
            res = f(*args, **kwargs)            

            session.clear()                  # Se ejecuta la funcion del endpoint requerido.
            return res                                             # Retorna el valor de la funcion.
        
        return wrapper



def connectPyMongo(host,db,user,password):
    client = MongoClient(host,
    username=user,
    password=password,
    authSource=db,
    authMechanism='SCRAM-SHA-256')
    mydb = client[db]
    return mydb


def connectMongoEngine(host,db,user,passw):
    try:
        conection=connect(host="mongodb://"+username+":"+password+"@"+host+"/xentric_db?authSource=admin")
        conection=connect(alias="conne_"+str(db),host="mongodb://"+user+":"+passw+"@"+host+"/"+db+"?authSource="+db)
        return "conne_"+str(db)
    except Exception as ex:
        logging.critical(ex)


def getPermission(token):
    AuthConfig=app.config["AuthConfig"]
    config=AuthConfig
    url = config["UrlToken"]
    payload='grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Auma-ticket&audience=flask_api&response_mode=permissions'    
    headers = {
    'Authorization':'Bearer '+str(token),
    'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if(response.status_code == 200):
        data=response.json()
        return data
    else:
        return []

def addUser(user,token):
    mydb = myclient["xentric_db"]
    mycol = mydb["user"]
    group=user["groups"]
    d=mycol.find_one({"$and": [{"client": group[0]}, {"user": user["preferred_username"]}]})
    if d is None:
        userName=""
        userLastname=""
        email=""
        if "given_name" in user:
            userName=user["given_name"]
        if "family_name" in user:
            userLastname=user["family_name"]
        if "email" in user:
            email=user["email"]   
        permissions=getPermission(token)
        data={"client":group[0],"user":user["preferred_username"],"name":userName,"last_name":userLastname,"email":email,"permission":permissions}
        mycol.insert_one(data)

def addRegister(user,resource,ip):
    mydb = myclient["xentric_db"]
    mycol = mydb["registers"]
    group=user["groups"]
    data={"client":group[0],"user":user["preferred_username"],"resource":resource,"date":datetime.now(),"ip_request":ip}
    mycol.insert_one(data)
