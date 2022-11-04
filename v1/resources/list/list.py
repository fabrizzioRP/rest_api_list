from datetime import datetime
from flask import jsonify, request,Response
from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse
from bson.objectid import ObjectId
import werkzeug, os
from bson import json_util
import json
import io
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


#Modelo de datos para configLists
campos_unicos = campos_con_valores_unicos(configuracion)
mongo_configlists = ConfigListModel(campos_unicos)

#Argumentos post de recurso list
list_post = reqparse.RequestParser()
list_post.add_argument('id_list',type=str, required=True, help="...")
list_post.add_argument('id_config',type=str, required=True, help="...")
list_post.add_argument('file', type=werkzeug.datastructures.FileStorage, required=False, location='files')
list_post.add_argument('description',type=str, required=False, default=None, help="...")

#Modelo de datos para list
mongo_lists = ListModel()

class Lists(Resource):
    
    #curl -X POST -F file=@"C:\test.txt" http://127.0.0.1:5000/list --form "id_config=xxx" --form "id_list=xxxx"
    @Auth.authenticate
    @dbAccess.pymongoAccess
    def post(self, creation_date=None):
        #Argumentos del request post
        argumentos = list_post.parse_args(); 
        
        #Verificar que id de lista no exista antes
        id_list = argumentos["id_list"]
        valid, error = mongo_lists.idlist_unique(id_list)
        if not valid:
            return {'message':error}, 400
        #mongo_lists.get(cliente, id_list)

        #Obtener configuracion de listas desde base de datos con id_config
        id_config = argumentos["id_config"]
        #Obtener config_list
        configlist, valid, error = mongo_configlists.get(id_config)
        if not valid:
            return {'message':error}, 400
        
        #Recuperar archivo 
        archivo = argumentos['file']
        filename = archivo.filename
        #Verificar si archivo es csv o txt
        formato = configlist["file_format"]
        if not filename.endswith('.'+formato):
            error = 'Archivo no tiene la extension "'+formato+'" que esta definida en la configuracion de listas.'
            return {'message':error}, 400
        #Cargar archivo
        if archivo == "":
            return {'message':'Archivo no contiene datos.'}, 400
        #Leer archivo
        archivo = archivo.read()
        #Obtener codec del archivo. Si archivo es muy grande 'detec' se pega, por eso esta el limite de 1000 caracteres.
        if len(archivo)>10000: codec = detect(archivo[:10000])['encoding']
        else: codec = detect(archivo)['encoding']
        #Verificar que la codificacion del archivo es la que se configuro para esta carga de lista.
        if configlist['file_codec'] and codec != configlist['file_codec'] and codec != 'ascii':
            error = f"El archivo esta codificado en '{codec}'. Pero la configuracion de lista indica que la codificacion debe ser '{configlist['file_codec']}'. Debe cambiar la configuracion de listas o la codificacion del archivo."
            logging.error(error)
            return {'message':error}, 400
        elif configlist['file_codec'] is None:
            configlist['file_codec'] = codec
        #Codificar archivo y convertir a lista
        archivo = archivo.decode(configlist['file_codec']).replace('\r','').split('\n')
        #validar nombres de campos de la lista
        names_field, valid, error = validar_nombres_lista(archivo, configlist)
        if not valid:
            return {'message':error}, 400
        #Validar datos del archivo
        logging.debug("archivo")
        logging.debug(archivo)
        logging.debug("id_list")
        logging.debug(id_list)
        logging.debug("configlist")
        logging.debug(configlist)

        try:
            list_data = validar_data(archivo, id_list, configlist)        
        except Exception as error:
            logging.error("error: "+str(error))
        #Guardar datos en mongo. Datos validos e invalidos.
        valid, error = mongo_lists.load_datalist(list_data)
        if not valid:
            return {'message':error}, 500
        #Retornar summary de carga.
        validos, invalidos, total = recuento(list_data)
        summary = {'valid rows':validos, 'invalid rows':invalidos, 'total':total}

        #Guardar propiedades de lista cargada
        fecha = datetime.now()
        if not creation_date: creation_date = fecha 
        lista_propiedades = {'id_list':id_list, 'id_config':id_config, 'filename':filename,'creation date':creation_date, 'modification_date':fecha, 'names_field':names_field, 'summary':summary,"config":configlist}
        valid, error = mongo_lists.register_list(lista_propiedades)
        if not valid:
            return {'message':error}, 500
        
        del lista_propiedades['_id']

        return jsonify(lista_propiedades)

    #http://localhost:5000/list                                 Devuelve todas las listas del cliente
    #http://localhost:5000/list/nombrelista?start=1&limit=10    Devuelve los datos de una lista
    @Auth.authenticate  
    @dbAccess.pymongoAccess
    def get(self, id_list):
        logging.info("get lists")
        if id_list:        
            url = request.base_url
            args = request.args
            start = args['start'] if 'start' in args else 1
            limit = args['limit'] if 'limit' in args else 10
            results = mongo_lists.get(id_list, url, start, limit) 
        else:
            url = request.base_url
            args = request.args
            start = args['start'] if 'start' in args else 1
            limit = args['limit'] if 'limit' in args else 10
            results = mongo_lists.getall(url, start, limit) 
        return jsonify(results)

    #http://localhost:5000/list                 Borra todo
    #http://localhost:5000/list/nombrelista     Borra nombrelista
    @Auth.authenticate
    @dbAccess.pymongoAccess
    def delete(self, id_list):
        #Si existe un id la funcion elimina la configuracion de lista del id 
        if id_list:
            #validar que existe id_list en la base de datos
            #eliminar recurso
            valid, error = mongo_lists.delete(id_list)
            if not valid:
                return {"message": error}, 400
            return {"message": 'La lista "'+id_list+'" fue eliminada.'}, 200
        #Si no existe id la funcion retorna todas las listuraciones de lista
        else:
            valid, error = mongo_lists.delete(id_list)
            if not valid:
                return {"message": error}, 200
            else:
                deleted_count = error
                return {"message": 'Todas las listas fueron eliminadas.', "deleted_count":deleted_count}, 200


    #http://localhost:5000/list/nombrelista     
    #Sirve para cargar una lista de nuevo sin cambiar el id_lista. Se deben agregar argumentos de carga de lista, igual que en post.
    @Auth.authenticate
    @dbAccess.pymongoAccess
    def put(self, id_list):
        if not id_list: 
            return {"message": "Debe agregar id de la lista en url."}, 400
        exist_idlist = mongo_lists.exist_id(id_list)
        if not exist_idlist:
            return {"message": "No existe el id de la lista que desea actualizar."}, 400
        #id existe
        #encontrar fecha de creacion
        fecha = mongo_lists.get_fecha_creacion(id_list)
        #hash de id_list
        id_list_tmp = hashlib.sha1(id_list.encode()).hexdigest()
        #remplazar id_list en la base por el hash
        mongo_lists.rename_id(id_list, id_list_tmp)
        recurso = self.post(creation_date=fecha)
        #!si configuracion no es valida enviar mensaje de error
        #!si actualizacion fue correcta, eliminar recurso temporal y retornar recurso con fechas de creacion y modificacion
        self.delete(id_list_tmp)
        return recurso

class List(Resource):

    #http://localhost:5000/lista/id_lista 
    #obtiene los datos de una lista cargada en base de datos segun su id 
    @Auth.authenticate  
    @dbAccess.pymongoAccess
    def get(self, id_list):          
        results = mongo_lists.getOne(id_list) 
        return jsonify(results)

    #http://localhost:5000/lista/id_lista 
    #actualiza un campo de un registro de contacto de una lista, segun id_lista, row, e indice del array donde esta el campo
    @Auth.authenticate  
    @dbAccess.pymongoAccess
    def put(self, id_list):    
        try:
            body = request.get_json(force=True)

            id_config = body['id_config'] #id de configuracion
            id_list = body['id_list'] # id de lista
            row = body['row'] #numero de fila a actualizar
            registro = body['registro'] #datos de fila a actualizar

            #Obtener config_list
            configlist, valid, error = mongo_configlists.get(id_config)
            if not valid:
                logging.warning(error)
                return {'message':error}, 400  

            #se valida la data nueva del registro que despues se actualizara en base de datos
            try:
                data = validar_registro(registro, row, id_list, configlist)
            except Exception as error:
                logging.error(f'error1 : {error}')
                return {"message": "Error al realizar la validacion del nuevo dato"}, 400 

            #se actualiza el registro en la base de datos
            valid, error = mongo_lists.edit_data_List(id_list, row, data)
            if not valid:
                return {'message':error}, 500
            
        except Exception as error:
            logging.error(f'error2 : {error}')
            return {"message": "No existe los parametros necesarios para actualizar el registro de la lista"}, 400

    #http://localhost:5000/lista/id_lista 
    #elimina un registro de la lista
    @Auth.authenticate  
    @dbAccess.pymongoAccess
    def delete(self, id_list):  
        try:
            body = request.get_json(force=True)
            row = body['row'] #fila a eliminar+
            logging.info('row: '+str(row))

            if not id_list: 
                logging.debug(f"id_list: {id_list}")
                return {"message": "Debe agregar id de la lista en url."}, 400
            if not row or row==0: 
                logging.debug(f"row: {row}")
                return {"message": "Debe agregar la fila (row) que quiere borrar"}, 400
   
            valid, error = mongo_lists.delete_data_List(id_list, row)
            if not valid:
                return {"message": error}, 400
            return {"message": 'El registro en la lista "'+id_list+'" fue eliminado.'}, 200
            
        except Exception as error:
            logging.error(f"error2 : {error}")
            return {"message": "No existe los parametros necesarios para eliminar el registro de la lista"}, 400


class DownloadList(Resource):
    @Auth.authenticate
    @dbAccess.pymongoAccess
    def post(self):
        Parser = reqparse.RequestParser()
        Parser.add_argument('id_list', type=str)
        IdList = Parser.parse_args()["id_list"]
        ListObject = mongo_lists.GetList(IdList)
        
        if not ListObject:
            return {"message": "No existe la lista seleccionada"}, 400
        Extension = ListObject["config"]["file_format"]
        DataList = mongo_lists.GetDataList(IdList)
        Delimiter = ListObject["config"]["delimiter"]
        if DataList is None:
            return []
        if Extension == "txt":
            Text = ""
            for x in ListObject["names_field"]:
                Text = Text + x["fieldname"] + Delimiter
            
            if Text.endswith(Delimiter):
                Text = Text[:-1]
            Text = Text+"\n"
            for Data in DataList:
                Line = ""
                for x in Data["data"]:
                    if Line == "":
                        Line = x
                    else:
                        Line = Line + Delimiter+ x
                Text = Text + Line + "\n"
            
            File = io.StringIO(Text)
            headers = {
                'Content-Disposition': 'attachment; filename=output.txt',
                'Content-type': 'application/vnd.ms-excel'
            }
            return Response(File.getvalue(), mimetype='application/txt', headers=headers)
        elif Extension == "csv":
            Data = []
            for x in DataList:
                Data.append(x["data"])

            Data = pd.DataFrame(Data)
            Buffer = io.BytesIO()
            Head = []
            for x in ListObject["names_field"]:
                Head.append(x["fieldname"])
               
            Data.columns = Head
            Data.to_csv(Buffer, index=0)
            
            Headers = {
                'Content-Disposition': 'attachment; filename=outfile'+'.csv',
                'Content-type': 'text/csv'
            }
            
            return Response(Buffer.getvalue(), mimetype='text/csv', headers=Headers)
        
        


class ExportList(Resource):

    #http://localhost:5000/export_list/id_lista
    # Exporta todos los registros de una lista segun su  id_lista en un archivo CSV descargable  
    @Auth.authenticate  
    @dbAccess.pymongoAccess
    def get(self, id_list):          
        results = mongo_lists.export_data_List(id_list) 
        csv = results  
        response = make_response(csv)
        cd = 'attachment; filename='+id_list+'.csv'
        response.headers['Content-Disposition'] = cd 
        response.mimetype='text/csv'
        return response

class ListElement(Resource):
    @Auth.authenticate  
    @dbAccess.pymongoAccess
    def post(self):
        try:
            #req parser 
            parser = reqparse.RequestParser()
            parser.add_argument('data', action='append')
            parser.add_argument('id_list', type=str)
            parammeters=parser.parse_args()
            data = parammeters['data']
            dataParsed=""
            e=0
            limit=len(data)
            for x in data:
                if(e!=limit-1):
                    dataParsed=dataParsed+x+";"
                else:
                    dataParsed=dataParsed+x
                e=e+1
            archivo=[]
            archivo.append(dataParsed)
            idList = parammeters['id_list']
            Mongo = session['dbPyMongo']
            coleccion_lists = Mongo['lists'] 
            config=coleccion_lists.find_one({"id_list": idList})["config"]
            if(config==None):
                logging.warning(17)
                return {"message": "No existe la lista de la lista"}, 404
            config["delimiter"]=";"
            config["first_line_names"]=False
            list_data = validar_data(archivo, idList, config) 
            valid, error = mongo_lists.load_datalist(list_data)
            if not valid:
                return {'message':error}, 500
            return {"message": "La fila fue cargada correctamente"}, 200
            

            
            return "s"
        except Exception as error:
            return {"message": "Error al cargar la lista"}, 50
       