import pymongo
from pymongo import IndexModel, ASCENDING, DESCENDING
from bson import json_util
from bson.objectid import ObjectId
from flask import session
from v1.utils.paginated_list import get_paginated_list
from mongoengine.context_managers import switch_db
import pandas as pd
import logging
 

#config_list -> guarda los formatos de validacion de las listas. Se usa para validar los datos de una lista
#lists -> guarda los metadatos de una lista: nombre, tipo de archivo, nombre de los campos, total de datos
#data_list -> guarda el contenido de filas y campos de una lista, es decir los datos de una lista.

class ListModel:
    #Instancia coleccion y carga
    def __init__(self):
        #self.coleccion_datalist = Mongo('API_LISTS_data_list').collection
        #self.coleccion_lists = Mongo('API_LISTS_lists').collection
        return
    
    #Este metodo guarda los datos de la lista
    def load_datalist(self, datos):
        Mongo = session['dbPyMongo']
        coleccion_datalist = Mongo['data_list']
        try:
            coleccion_datalist.insert_many(datos)
        except Exception as error:
            logging.critical(f'error1 : {error}')
            error='No se lograron guardar los datos en la base de datos.'
            return False, error        
        return True, None

    #Este metodo guarda los metadatos de la lista
    def register_list(self, datos):
        Mongo = session['dbPyMongo']
        coleccion_lists = Mongo['lists']
        try:
            coleccion_lists.insert_one(datos)
        except Exception as error:
            logging.critical(f'error2 : {error}')
            error='No se lograron guardar los datos en la base de datos.'
            return False, error        
        return True, None
    
    #Este metodo verifica si el id de lista ya existe
    def idlist_unique(self, id_list):
        Mongo = session['dbPyMongo']
        coleccion_lists = Mongo['lists']
        valid=True; error=None
        exist = coleccion_lists.find_one({'id_list':id_list}, {'_id':1})
        if exist:
            valid=False
            error='El id de lista ya existe. Ingrese uno nuevo.'
        return valid, error

    #Este metodo retorna los datos de una lista en particular
    def get(self, id_list, url=None, start=None, limit=None):
        #Conexion a base de datos.
        Mongo = session['dbPyMongo']
        coleccion_lists = Mongo['lists']
        coleccion_datalist = Mongo['data_list']
        valid=True; error=''
        recurso = coleccion_lists.find_one({'id_list':id_list})  
        if not recurso:
            valid=False
            error = 'No se encontró la lista identificada como "'+id_list+'". Asegurese de usar un valor que ya exista.'
            return recurso, valid, error        
        else:
            recurso = coleccion_datalist.find({'id_list':id_list}, {'_id':0})      
            resultado = get_paginated_list(recurso, url, start, limit)
            return resultado

    #Este metodo retorna todas las listas del cliente
    def getall(self, url=None, start=None, limit=None):
        Mongo = session['dbPyMongo']
        coleccion_lists = Mongo['lists']
        valid=True; error=''
        recurso = coleccion_lists.find({}, {'_id':0})  
        if not recurso:
            valid=False
            error = 'No existen listas cargadas.'
            return recurso, valid, error        
        else:
            resultado = get_paginated_list(recurso, url, start, limit)
            return resultado

    #Este metodo retorna una sola lista de todas por id de lista y id de cliente
    def getOne(self, id_list):
        Mongo = session['dbPyMongo']
        coleccion_lists = Mongo['lists']
        valid=True; error=''
        recurso = coleccion_lists.find_one({'id_list':id_list}, {'_id':0})  
        if not recurso:
            valid=False
            error = 'No se encontró la lista identificada como "'+id_list+'". Asegurese de usar un valor que ya exista.'
            return recurso, valid, error        
        else:
            return recurso


    def delete(self, id_list):
        #Conexion a base de datos.
        Mongo = session['dbPyMongo']
        coleccion_lists = Mongo['lists']
        coleccion_datalist = Mongo['data_list']
        valid=True; error=''
        if id_list:
            result = coleccion_lists.delete_one({'id_list':id_list})
            if not result.deleted_count:
                valid=False
                error = 'No se encontró la lista identificada como "'+id_list+'". Asegurese de usar un valor que ya exista.'
                return valid, error                
            coleccion_datalist.delete_many({'id_list':id_list})
            return valid, error
        else:
            result = coleccion_lists.delete_many({})
            deleted_count = result.deleted_count
            if not deleted_count:
                valid=False
                error='No existen recursos para ser borrados.'
                return valid, error
            coleccion_datalist.delete_many({})
            return valid, deleted_count

    def delete_data_List(self, id_list, row):   
        #Conexion a base de datos.
        Mongo = session['dbPyMongo']
        coleccion_datalist = Mongo['data_list']
        valid=True; error=''
        try:
            coleccion_datalist.delete_one({'id_list':id_list, 'row': row})
        except Exception as error:
            logging.error(f'error : {error}')
            error='No se pudo eliminar el registro en la base de datos.'
            return False, error        
        return True, None  

    def exist_id(self, id_list):#Conexion a base de datos.
        Mongo = session['dbPyMongo']
        coleccion_lists = Mongo['lists']
        recurso = coleccion_lists.find_one({'id_list':id_list}, {'_id':1})  
        return bool(recurso)    

    def rename_id(self, id_list, id_new):  
        #Conexion a base de datos.
        Mongo = session['dbPyMongo']
        coleccion_lists = Mongo['lists']
        coleccion_datalist = Mongo['data_list']      
        coleccion_lists.update_one({'id_list':id_list}, {'$set': {'id_list':id_new}})
        coleccion_datalist.update_many({'id_list':id_list}, {'$set': {'id_list':id_new}})
        return

    def get_fecha_creacion(self, id_list):
        #Conexion a base de datos.
        Mongo = session['dbPyMongo']
        coleccion_lists = Mongo['lists']
        dato = coleccion_lists.find_one({'id_list':id_list}, {'_id':0, 'creation date':1})
        fecha = dato['creation date']
        return fecha    

    def edit_data_List(self, id_list, row, data):   
        #Conexion a base de datos.
        Mongo = session['dbPyMongo']
        coleccion_datalist = Mongo['data_list']
        try:
            coleccion_datalist.update_one({'id_list':id_list, 'row': row}, {'$set': data})
        except Exception as error:
            logging.error(f'error1 : {error}')
            error='No se pudo actualizar el registro en la base de datos.'
            return False, error        
        return True, None  


    def export_data_List(self, id_list):     
        #Conexion a base de datos.
        Mongo = session['dbPyMongo']
        coleccion_lists = Mongo['lists']
        coleccion_datalist = Mongo['data_list']   
        recurso = coleccion_datalist.find({'id_list': id_list}, {'_id': 0, 'data': 1, 'valid': 1, 'error': 1 })
        recurso2 = coleccion_lists.find_one({'id_list': id_list}, {'_id': 0, 'names_field': 1})
        lista = list(recurso)
        cabeceras = recurso2
        # print(cabeceras)

        listado = []
        for idx, val in enumerate(lista):
            diccionario = {}
            for idx2, val2 in enumerate(val['data']):
                diccionario[ cabeceras['names_field'][idx2]['fieldname'] ] = val2

            diccionario['valid'] = val['valid']
            diccionario['error'] = val['error']
            listado.append(diccionario)

        #print(listado)
        
        df = pd.DataFrame(listado)
        return df.to_csv(index=False, sep=";", encoding='utf-8')




    def getaCampaignList(self,idCampaign):
        Mongo = session['dbPyMongo']
        coleccion_lists = Mongo['campaign_lists']
        valid=True; error=''
        recurso = coleccion_lists.find({"id_campaign":ObjectId(idCampaign)},{'_id': False})  
        if not recurso:
            return []   
        else:
            return recurso
    
    def GetList(self, IdList):
        Mongo = session['dbPyMongo']
        ColectionLists = Mongo['lists']
        Resource = ColectionLists.find_one({'id_list':IdList})
        if Resource is not None:
            return Resource
        return False
    
    def GetDataList(self, IdList):
        Mongo = session['dbPyMongo']
        ColectionLists = Mongo['data_list']
        Resource = ColectionLists.find({'id_list':IdList})
        if Resource is not None:
            return Resource
        return False


