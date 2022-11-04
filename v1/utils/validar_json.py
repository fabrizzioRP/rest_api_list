from pprint import pprint
import logging

'''configuracion = {"id_config":{"datatype":str,
                              "requerido":True,
                              "valores_permitidos":[],
                              "valores_prohibidos":[],
                              "valores_unicos":True,
                              "valor_default":None},
                 "first_line_names":{"datatype":bool,
                              "requerido":False,
                              "valores_permitidos":[],
                              "valores_prohibidos":[],
                              "valores_unicos":True,
                              "valor_default":True},
                 "fields_list":{"datatype":list,
                              "requerido":True,
                              "valor_default":None,
                              "elementos_unicos":True,
                              "datatype_elemento":dict,
                              "config_elemento":{"field_name":{"datatype":str,
                                                               "requerido":False,
                                                               "valores_permitidos":[],
                                                               "valores_prohibidos":[],
                                                               "valores_unicos":True,
                                                               "valor_default":id},
                                                 "datatype":{  "datatype":str,
                                                               "requerido":False,
                                                               "valores_permitidos":['int','str','bool','date','datetime'],
                                                               "valores_prohibidos":[],
                                                               "valores_unicos":False,
                                                               "valor_default":'str'},
                                                 "fieldtype":{ "datatype":str,
                                                               "requerido":False,
                                                               "valores_permitidos":['user','phone','other'],
                                                               "valores_prohibidos":[],
                                                               "valores_unicos":False,
                                                               "valor_default":'other'},
                                                 "config_phone":{"datatype":dict,
                                                                 "requerido":False,
                                                                 "valor_default":{"prefix": "", "digits": -1},
                                                                 "config_elemento":{ "prefix": {"datatype":str,
                                                                                                "requerido":False,
                                                                                                "valores_permitidos":[],
                                                                                                "valores_prohibidos":[],
                                                                                                "valores_unicos":False,
                                                                                                "valor_default":''},
                                                                                     "digits": {"datatype":int,
                                                                                                "requerido":False,
                                                                                                "valores_permitidos":[],
                                                                                                "valores_prohibidos":[0,1,2,3,4,5],
                                                                                                "valores_unicos":False,
                                                                                                "valor_default":-1}}},
                                                 "skip":{      "datatype":bool,
                                                               "requerido":False,
                                                               "valores_permitidos":[True,False],
                                                               "valores_prohibidos":[],
                                                               "valores_unicos":False,
                                                               "valor_default":False}}},
                 "file_format":{"datatype":str,
                              "requerido":False,
                              "valores_permitidos":['csv','txt'],
                              "valores_prohibidos":[],
                              "valores_unicos":False,
                              "valor_default":'csv'},
                 "file_codec":{"datatype":str,
                              "requerido":False,
                              "valores_permitidos":[],
                              "valores_prohibidos":[],
                              "valores_unicos":False,
                              "valor_default":None},                                                
                 "delimiter":{"datatype":str,
                              "requerido":True,
                              "valores_permitidos":[';','.',',',' ','\t'],
                              "valores_prohibidos":[],
                              "valores_unicos":False,
                              "valor_default":';'}
                 }




datos= {"id_config": "xxx",
    "first_line_names":true,  
    "fields_list": [    { "field_name": "telefono",  
                           "datatype": "int", 
                           "fieldtype": "phone",
                           "config_phone": {"prefix": "",
                                            "digits": 0},                        
                           "skip": False},

                         { "field_name": "contacto",  
                           "datatype": "string", 
                           "fieldtype": "user",
                           "skip": False },
              
                         { "field_name": "fecha",  
                           "datatype": "datetime", 
                           "fieldtype": "other",
                           "skip": False },

                         { "field_name": "direccion",  
                           "datatype": 'string', 
                           "fieldtype": "other",
                           "skip": False },],

  "file_format": "csv",
  "file_codec": "utf-8", 
  "delimiter": ";"}'''


def validar(configuracion, datos, ruta='', valid=True, errores=''):
    
    for campo in datos.keys():
        if not validar_campos(campo, configuracion):
            valid = False
            errores += 'El nombre "'+campo+'" que ingreso como campo no es valido. '

    #print('RUTA = ',ruta)
    for campo, config in configuracion.items():

        #Campo no fue agregado en datos
        if not campo in datos:
            #Si el campo no fue agregado pero es obligatorio, enviar error.
            if config['requerido']:
                valid = False
                errores += 'El campo "'+ruta+'.'+campo+'" es obligatorio. Debe agregarlo. '
                continue
            #Si el campo no fue agregado pero es opcional, agregar valor por defecto.
            else:
                #print('Se agrego valor por defecto a campo "'+ruta+'.'+campo+'".')
                datos[campo] = config['valor_default']

        #Campo fue agregado en datos        
        else:
            dato = datos[campo]
            datatype = config['datatype']
            #El tipo de datos del objeto no corresponde al definido en la configuracion
            if not datatype==type(dato):
                valid = False                
                errores += 'Error. El dato que ingreso en el campo "'+ruta+'.'+campo+'" es de tipo "'+type(dato).__name__+'". La configuracion requiere que sea "'+datatype.__name__+'".\n'
                continue
            #El tipo de datos del objeto analizado es el que corresponde a la configuracion
            else:
                #Si el objeto analizado es un diccionario
                if datatype is dict:
                    new_ruta = ruta + '.'  + campo if ruta else campo
                    #print('ruta = '+ruta)
                    datos_dict, valid, errores = validar(configuracion=config['config_elemento'], datos=dato, ruta=new_ruta,valid=valid, errores=errores)
                    datos[campo]=datos_dict
                #Si el objeto analizado es una lista
                elif datatype is list:
                    datos_list = []
                    datatype_list = config["datatype_elemento"]
                    elementos_unicos = config["elementos_unicos"]
                    # CHECKEAR QUE NO HAYAN ELEMENTOS REPETIDOS EN LA LISTA SI ES QUE FUE CONFIGURADO ASI
                    if elementos_unicos and not datatype_list==dict and not datatype_list==list:
                        unique=checkIfDuplicates(dato)
                        if not unique:
                            valid = False
                            errores += 'Error. Las configuraciones de la lista "'+ruta +'.'+ campo+'" no deben estar repetidas. '
                    #SI UNO DE LOS CAMPOS DEL DICCIONARIO DE LA LISTA ESTA CONFIGURADO COMO UNICO, VERIFICAR QUE NO SE REPITA
                    if datatype_list is dict:
                        campos_unicos = campos_con_valores_unicos(config['config_elemento'])
                        set_data = []
                        for campo_unico in campos_unicos:
                            for dato_list in dato:
                                if campo_unico in dato_list:
                                    if dato_list[campo_unico] in set_data:
                                        valid = False
                                        errores+='Los datos del campo "'+ruta+'.'+campo+'.'+campo_unico+'" no deben estar repetidos en los elementos de la lista "'+ruta +'.'+ campo+'". '
                                    else:
                                        set_data.append(dato_list[campo_unico])

                    #elemento_unico=[]
                    c=0
                    for dato_list in dato:
                        #Esto es para saber la ruta del nodo donde se esta evaluando
                        new_ruta = ruta + '.'  + campo +'.['+str(c)+']' if ruta else campo+'.['+str(c)+']'
                        #Si el elemento de la lista no es del tipo definido en la configuracion, acusar error y seguir con siguiente elemento.
                        if type(dato_list)!=datatype_list:
                            valid = False                
                            errores += 'Error. El elemento '+str(c)+' de la lista que esta en el campo "'+new_ruta+'" es de tipo "'+type(dato_list).__name__+'". La configuracion requiere que sea "'+datatype_list.__name__+'".\n'
                            datos_list.append(dato_list)
                            c+=1
                            continue
                        else:                
                            dato_list, valid, errores = validar(configuracion=config['config_elemento'], datos=dato_list, ruta=new_ruta, valid=valid, errores=errores)
                            datos_list.append(dato_list)
                            c+=1
                            
                #Cualquier tipo de datos que no sea dict o list
                else:
                    logging.debug(f"ruta,campo,dato = {ruta}.{campo}: {dato}")

                    valores_permitidos = config["valores_permitidos"]
                    valores_prohibidos = config["valores_prohibidos"]
                  
                    #Todos los valores permitidos, excepto los ilegales: [All], [a,b,c,..]
                    if dato in valores_prohibidos:
                        valid = False
                        valores_prohibidos = str(valores_prohibidos)[1:-1]
                        errores += 'Error. Los valores '+valores_prohibidos+', no estan permitidos en el campo '+ruta+'.'+campo+' .\n'

                    #Solo algunos valores permitidos: [a,b,c,..],[]
                    if valores_permitidos and not dato in valores_permitidos:
                        valid = False
                        valores_permitidos = str(valores_permitidos)[1:-1]
                        errores += 'Error. Solo los valores '+valores_permitidos+', estan permitidos en el campo '+ruta+'.'+campo+' .\n'

      
    return datos, valid, errores
                
#Valida que los nombres de los campos de entrada correspondan a los configurados
#Esta basado en el json de configuracion
def validar_campos(campo, configuracion):    

    for key, config in configuracion.items():
        if key == campo:
            return True
        if 'config_elemento' in config:
            result = validar_campos(campo, config['config_elemento'])
            if result:
                return True

    return False

#Retorna que campos estan configurados para no tener valores repetidos
def campos_con_valores_unicos(configuracion):
    valores_unicos=[]
    for key, value in configuracion.items():
        if 'valores_unicos' in value and value['valores_unicos'] is True:
            valores_unicos.append(key)
    return valores_unicos
#datos, valid, errores = validar(configuracion, datos)
#print(errores)

#Checkea si uan lista tiene o no elementos duplicados
def checkIfDuplicates(lista):
    ''' Check if given list contains any duplicates '''    
    setOfElems = set()
    for elem in lista:
        if elem in setOfElems:
            return True
        else:
            setOfElems.add(elem)         
    return False

            
