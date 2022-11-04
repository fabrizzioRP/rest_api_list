import pymongo
from pymongo import IndexModel, ASCENDING, DESCENDING
from bson import json_util
from bson.objectid import ObjectId
from pprint import pprint
from flask import session
from v1.utils.paginated_list import get_paginated_list

#config_list -> guarda los formatos de validacion de las listas. Se usa para validar los datos de una lista
#lists -> guarda los metadatos de una lista: nombre, tipo de archivo, nombre de los campos, total de datos
#data_list -> guarda el contenido de filas y campos de una lista, es decir los datos de una lista.

class ConfigListModel:
    #Instancia coleccion y carga
    def __init__(self, valores_unicos=[]):
        '''
        Mongo = session['dbPyMongo']
        coleccion = Mongo['config_list']
        #Se le crea un indice a los campos con valores unicos para que lanze error cuando se ingrese un valor repetido.
        if valores_unicos:
            for campo in valores_unicos:
                coleccion.create_index([(campo, ASCENDING)], unique=True)
        '''
        return
                    
    def post(self, fecha_creacion, fecha_modificacion, recurso):
        #Conexion a base de datos.
        Mongo = session['dbPyMongo']
        coleccion = Mongo['config_list']
        numero = coleccion.count_documents({})+1
        #documento = {"cliente":cliente, "id_config":id_config, "numero":numero, "fecha_creacion":fecha_creacion, "fecha_modificacion":fecha_modificacion, "recurso":recurso}
        documento = {"numero":numero, "fecha_creacion":fecha_creacion, "fecha_modificacion":fecha_modificacion}
        for key, value in recurso.items():
            documento[key]=value
        try:              
            coleccion.insert_one(documento)
        #Este error aparece cuando se ingresa un valor repetido a "id_config".
        except pymongo.errors.DuplicateKeyError as error:
            try:
                campo = error.args[0].split(':')[2].split()[0][:-2]
                valor = error.args[0].split(':')[4][:-1].strip()
                error = 'El valor '+valor+' que envio en el campo "'+campo+'" ya existe. Ingrese uno nuevo.'
            except:
                error='Ingreso en uno de los campos un valor que ya fue ingresado en una configuracion anterior. '
            return False, error

        return True, ''

    def get(self, id_config, url=None, start=None, limit=None):
        #Conexion a base de datos.
        Mongo = session['dbPyMongo']
        coleccion = Mongo['config_list']
        if id_config:
            valid=True; error=''
            recurso = coleccion.find_one({'id_config':id_config}, {'_id':0, 'cliente':0})        
            if not recurso:
                valid=False
                error = 'No se encontró la configuracion de listas identificada como "'+id_config+'". Asegurese de usar un valor que ya exista.'
            return recurso, valid, error        
        else:
            recurso = coleccion.find({}, {'_id':0, 'cliente':0})      
            resultado = get_paginated_list(recurso, url, start, limit)
            return resultado

    def exist_id(self, id_config):
        #Conexion a base de datos.
        Mongo = session['dbPyMongo']
        coleccion = Mongo['config_list']
        recurso = coleccion.find_one({'id_config':id_config}, {'_id':1})  
        return bool(recurso)    

    def rename_id(self, id_config, id_new):
        #Conexion a base de datos.
        Mongo = session['dbPyMongo']
        coleccion = Mongo['config_list']
        coleccion.update_one({'id_config':id_config}, {'$set': {'id_config':id_new}})
        return

    def get_fecha_creacion(self, id_config):
        #Conexion a base de datos.
        Mongo = session['dbPyMongo']
        coleccion = Mongo['config_list']
        dato = coleccion.find_one({'id_config':id_config}, {'_id':0, 'fecha_creacion':1})
        fecha = dato['fecha_creacion']
        return fecha        

    def delete(self, id_config):
        #Conexion a base de datos.
        Mongo = session['dbPyMongo']
        coleccion = Mongo['config_list']
        valid=True; error=''
        if id_config:
            result = coleccion.delete_one({'id_config':id_config})
            if not result.deleted_count:
                valid=False
                error = 'No se encontró la configuracion de listas identificada como "'+id_config+'". Asegurese de usar un valor que ya exista.'
            return valid, error
        else:
            result = coleccion.delete_many({})
            deleted_count = result.deleted_count
            if not deleted_count:
                valid=False
                error='No existen recursos para ser borrados.'
                return valid, error
            return valid, deleted_count

