from datetime import datetime
import hashlib
from flask import jsonify, request
from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse
import json
from v1.resources.auth.authorization import Auth
from v1.resources.auth.dbDecorator import dbAccess
from v1.resources.list.validacion_confgLists import configuracion
from v1.models.list.configlist import ConfigListModel
from v1.models.list.list import ListModel
from v1.utils.validar_json import validar, campos_con_valores_unicos
# from db import Mongo


#Modelo de datos para configLists
campos_unicos = campos_con_valores_unicos(configuracion)
mongo_configlists = ConfigListModel(campos_unicos)


#curl en windows
#curl -X POST http://localhost:5000/configlist -d "{\"id_config\":\"config_4\",\"first_line_names\":true,\"fields_list\":[{\"field_name\":\"telefono\",\"datatype\":\"int\",\"fieldtype\":\"phone\",\"config_phone\":{\"prefix\":\"\",\"digits\":0},\"skip\":false},{\"datatype\":\"string\",\"fieldtype\":\"user\",\"skip\":false},{\"field_name\":\"fecha\",\"datatype\":\"datetime\",\"fieldtype\":\"other\",\"skip\":false},{\"field_name\":\"\",\"datatype\":\"string\",\"fieldtype\":\"other\",\"skip\":false}],\"file_format\":\"csv\",\"file_codec\":\"utf-8\",\"delimiter\":\";\"}"
class ConfigLists(Resource):
    @Auth.authenticate  
    @dbAccess.pymongoAccess
    def post(self, id_config=None, fecha_creacion=None):
        #Recuperar argumentos de json en body del request
        argumentos = request.get_json(force=True)
        if id_config: argumentos['id_config'] = id_config
        #Validar argumentos. Agregar los que son por default        
        recurso, valid, error = validar(configuracion, argumentos)
        #Al menos un campo de field_list debe ser phone y otro user
        valid, error = check_fieldlist(argumentos)
        #Retornar error si existe
        if not valid:
            return {"message": error}, 400
        #Crear y guardar recurso en base de datos
        #id_config, numero, fecha_creacion, fecha_modificacion, recurso
        fecha_created = datetime.now() if not fecha_creacion else fecha_creacion
        fecha_mod = datetime.now()
        valid, error = mongo_configlists.post(fecha_creacion=fecha_created, fecha_modificacion=fecha_mod, recurso=recurso)
        if not valid:
            return {"message": error}, 400
        #Devolver datos del recurso creado.
        return recurso
        
    @Auth.authenticate  
    @dbAccess.pymongoAccess
    def get(self, id_config):
        #Si existe un id la funcion retorna la configuracion correspondiente a esa lista 
        if id_config:
            #validar que existe id_config en la base de datos
            #retornar valores
            recurso, valid, error = mongo_configlists.get(id_config)
            if not valid:
                return {"message": error}, 400
            return jsonify(recurso)
        #! Si no existe id la funcion retorna todas las configuraciones de lista.
        #! Intentar usar paginacion.
        else:
            url = request.base_url
            args = request.args
            start = args['start'] if 'start' in args else 1
            limit = args['limit'] if 'limit' in args else 2
            results = mongo_configlists.get(id_config, url, start, limit)        
            return jsonify(results)
   
    @Auth.authenticate  
    @dbAccess.pymongoAccess      
    def put(self, id_config):
        if not id_config: 
            return {"message": "Debe agregar id de configuracion en url."}, 400
        exist_idconfig = mongo_configlists.exist_id(id_config)
        if not exist_idconfig:
            return {"message": "No existe el id de la configuracion que desea actualizar."}, 400
        #id existe
        #encontrar fecha de creacion
        fecha = mongo_configlists.get_fecha_creacion(id_config)
        #hash de id_config
        id_config_tmp = hashlib.sha1(id_config.encode()).hexdigest()
        #remplazar id_config en la base por el hash
        mongo_configlists.rename_id(id_config, id_config_tmp)
        recurso = self.post(id_config=id_config, fecha_creacion=fecha)
        #!si configuracion no es valida enviar mensaje de error
        #!si actualizacion fue correcta, eliminar recurso temporal y retornar recurso con fechas de creacion y modificacion
        self.delete(id_config_tmp)
        return recurso

    @Auth.authenticate  
    @dbAccess.pymongoAccess    
    def delete(self, id_config):
        #Si existe un id la funcion elimina la configuracion de lista del id 
        if id_config:
            #validar que existe id_config en la base de datos
            #eliminar recurso
            valid, error = mongo_configlists.delete(id_config)
            if not valid:
                return {"message": error}, 400
            return {"message": 'La configuracion de lista "'+id_config+'" fue eliminada.'}, 200
        #Si no existe id la funcion retorna todas las configuraciones de lista
        else:
            valid, error = mongo_configlists.delete(id_config)
            if not valid:
                return {"message": error}, 200
            else:
                deleted_count = error
                return {"message": 'Todas las configuraciones de lista fueron eliminadas.', "deleted_count":deleted_count}, 200
        

        



def check_fieldlist(argumentos):
    campos = argumentos['fields_list']
    valid=True; errores = ''
    phone = False; user = False    
    for campo in campos:
        fieldtype = campo['fieldtype']
        if fieldtype=='phone':
            phone = True
        if fieldtype=='user':
            user = True
    if not phone:
        valid = False
        #salto de linea en errores 
        errores += 'Al menos debe existir un valor "phone"  en el tipo de campo '
    if not user:
        if errores != '':
            errores += 'y '
        valid = False
        errores += 'Al menos debe existir un valor "user" en el tipo de campo.'

    return valid, errores
    