from datetime import datetime
from flask import jsonify, request
from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse
from bson.objectid import ObjectId
import werkzeug, os
import json
from flask import session
import hashlib
from chardet import detect #Modulo no nativo
from v1.resources.auth.authorization import Auth
from v1.resources.auth.dbDecorator import dbAccess
from v1.resources.list.validacion_confgLists import configuracion
from v1.resources.list.validacion_listas import validar_data, validar_nombres_lista, recuento, validar_registro
from v1.models.list.list import ListModel
from v1.models.list.configlist import ConfigListModel
from v1.utils.validar_json import validar, campos_con_valores_unicos
from mongoengine.context_managers import switch_db
# from db import Mongo
import pymongo
import pandas as pd
from flask import make_response  

import logging


#Modelo de datos para list
mongo_lists = ListModel()

class CampaignList(Resource):
    
    #curl -X POST -F file=@"C:\test.txt" http://127.0.0.1:5000/list --form "id_config=xxx" --form "id_list=xxxx"
    @Auth.authenticate  
    @dbAccess.pymongoAccess
    def get(self, creation_date=None):
        #obtener parametros desde la url
        parser = reqparse.RequestParser()
        parser.add_argument('id_campaign', type=str, required=True,location="args", help="Falta id_config")
        data=parser.parse_args()
        resp=mongo_lists.getaCampaignList(data['id_campaign'])
        resp=pd.DataFrame(resp,columns= ['id_contact', 'id_phone','contact_details'])
        logging.debug(resp)
        resp=resp.to_json(orient='records')
        return json.loads(resp)
        

       