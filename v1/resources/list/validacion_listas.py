import logging
import re
import time
from datetime import datetime
import collections


def validar_nombres_lista(lista, configuracion):

    #Si first_line es verdadero se le dara preferencia a esos nombres antes que a los de la configuracion.
    first_line = configuracion["first_line_names"]
    field_list = configuracion["fields_list"]
    field_length = len(field_list)
    delimitador = configuracion['delimiter']

    #VALIDAR QUE ESTEN EL NUMERO DE CAMPOS CORRECTOS
    if first_line:
        nombres_field = lista[0].strip()
        # Se utiliza la expresión regular para que no separe si el delimitador está dentro de comillas
        nombres_field = re.split(f"{delimitador}(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", nombres_field)
        nombres_field = [s.strip().strip('"') for s in nombres_field]
        #nombres_field = nombres_field.split(delimitador)
        #Verifica que todos los nombres de la primera fila esten con la cantidad de campos configurada y no sean vacios
        if len(nombres_field)!=field_length or not all(i for i in nombres_field):
            valid=False
            error='Primera fila de archivo no contiene los '+str(field_length)+' campos que fueron configurados en "field_list". '
            return None, valid, error
    #AGREGAR NOMBRES DE LISTAS QUE FALTEN EN CONFIGURACION COMO "field_i"
    else:
        nombres_field = []
        for i, field in enumerate(field_list):
            i+=1
            if 'field_name' in field:
                field_name = field["field_name"]
                if field_name:
                    nombres_field.append(field_name)
                else:
                    nombres_field.append('field_'+str(i))
            else:
                nombres_field.append('field_'+str(i))
    
    #Esto es para datos del return.
    names_field = []
    for i, field in enumerate(field_list):
        fieldtype = field["fieldtype"]
        datatype = field["datatype"]
        skip = field["skip"]
        #Toma en cuenta skip
        if skip:
            continue
        data_field = {'fieldname':nombres_field[i], "datatype":datatype, "fieldtype":fieldtype}
        names_field.append(data_field)

    return names_field, True, ''
    

def validar_data(lista, id_lista, configuracion):

    first_line = configuracion["first_line_names"]
    field_list = configuracion["fields_list"]
    field_length = len(field_list)
    delimitador = configuracion['delimiter']

    if first_line:
        lista.pop(0)

    list_data = []
    for n, fila in enumerate(lista):
        #Ya que el contador n del for comienza en cero, se le suma 1 o 2 para que coincida con la numeracion de la fila en el archivo.
        if first_line: n+=2
        else: n+=1
        #split por delimitador
        #fila = fila.split(delimitador)
        if fila == "":
            continue
        # Se utiliza la expresión regular para que no separe si el delimitador está dentro de comillas
        fila = re.split(f"{delimitador}(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", fila)
        fila = [s.strip().strip('"') for s in fila]
        #validar cantidad correcta de campos
        if len(fila)!=field_length:
            #Enviar data a mongo
            error = 'La cantidad de campos no coincide con la definida en la configuracion de listas.'
            data = {'id_list':id_lista, 'row':n, 'valid':False, 'error':error, 'data':fila}
            list_data.append(data)
            logging.warning(f"ok1 {n} {fila}")
            continue

        datos_fila = []
        valid=True
        errores = ''
        phone = ''
        contact = ''
        #recorrido es por la configuracion de las listas. Para los datos se usa el indice i
        for i, field in enumerate(field_list):
            
            fieldtype = field["fieldtype"]
            datatype = field["datatype"]
            skip = field["skip"]
            if skip:
                continue
            #Validar dato
            dato = fila[i]
            isPhone=False
            if fieldtype=='phone':
                prefix = field["config_phone"]["prefix"]
                digits = field["config_phone"]["digits"]                
                valido, error = validate_phone(dato, prefix, digits)
                #import logging
                logging.debug("dato: "+str(dato)[0])
                if str(dato)[0]!='+':
                    phone =  "+"+str(dato)
                    dato =  "+"+str(dato)
                else:
                    phone = str(dato)
                    dato=dato

            if fieldtype in ['user']:
                contact = fila[i]
                
            if fieldtype in ['user','other']:                
                valido, error = validate_data(dato, datatype)

            if error: errores += 'Columna '+str(i+1)+': '+error+' '
            #Transformar dato
            if valido:
                dato = transformar_dato(dato, datatype)
            #Agregar dato a lista
            valid*=valido
           
            datos_fila.append(dato)

        data = {'id_list':id_lista, 'row':n, 'valid':bool(valid), 'error':errores.strip(),'id_contact':contact, 'id_phone':phone, 'data':datos_fila}
        list_data.append(data)
        
    return list_data

def validar_registro(registro, row, id_lista, configuracion):
    field_list = configuracion["fields_list"]
    field_length = len(field_list)

    fila = registro

    #validar cantidad correcta de campos
    if len(fila)!=field_length:
        #Enviar data a mongo
        error = 'La cantidad de campos no coincide con la definida en la configuracion de listas.'
        data = {'id_list':id_lista, 'row':row, 'valid':False, 'error':error, 'data':fila}
    else:
        datos_fila = []
        valid=True
        errores = ''
        #recorrido es por la configuracion de las listas. Para los datos se usa el indice i
        for i, field in enumerate(field_list):
            
            fieldtype = field["fieldtype"]
            datatype = field["datatype"]
            skip = field["skip"]
            if skip:
                continue
            #Validar dato
            dato = fila[i]
            if fieldtype=='phone':
                prefix = field["config_phone"]["prefix"]
                digits = field["config_phone"]["digits"]                
                valido, error = validate_phone(dato, prefix, digits)
                
            if fieldtype in ['user','other']:                
                valido, error = validate_data(dato, datatype)

            if error: errores += 'Columna '+str(i+1)+': '+error+' '
            #Transformar dato
            if valido:
                dato = transformar_dato(dato, datatype)
            #Agregar dato a lista
            valid*=valido
            datos_fila.append(dato)

        data = {'id_list':id_lista, 'row':row, 'valid':bool(valid), 'error':errores.strip(), 'data':datos_fila}
    
    return data
    



def recuento(list_data):
    valid = [data['valid'] for data in list_data]
    frequency=collections.Counter(valid)
    validos = frequency.get(True)
    if validos is None:
        validos = 0

    invalidos = frequency.get(False)
    if invalidos is None:
        invalidos = 0

    total = validos+invalidos
    return validos, invalidos, total

def transformar_dato(data, datatype):

    if datatype in ['int','numero', 'number', 'integer', 'entero']:
        data = data.replace('+','').replace(',','')
        if '.' in data:
            data = float(data)
        else:
            data = int(data)

    if datatype in ['bool', 'boolean', 'booleano', 'boleano']:
        data = data.lower()
        if data in ['true','verdadero','cierto','0']:
            data = True
        elif data in ['false','falso','1']:
            data = False


    if datatype in ['date', 'fecha']:
        
        formatos = ['%d/%m/%Y', '%d/%m/%Y', '%m/%d/%Y', '%m/%d/%Y',
                    '%d-%m-%y', '%d-%m-%Y', '%m-%d-%y', '%m-%d-%Y',
                    '%d %m %y', '%d %m %Y', '%m %d %y', '%m %d %Y']

        for format in formatos:
            try:
                data = time.strptime(data, format)
            except:
                pass

    if datatype in ['datetime', 'time', 'hora']:

        data = datetime.strptime(data, "%Y-%m-%d %H:%M:%S")


    return data    
    
def validate_phone(phone, prefix, digits):

    valid=True
    error=None

    if phone.startswith('+'): phone = phone[1:]
    if prefix.startswith('+'): prefix = prefix[1:]

    if not phone:
        valid = False
        error = 'Dato vacio.'
        return valid, error
    

    if not phone.startswith(prefix):
        valid = False
        error = 'Dato no comienza con prefijo '+prefix+'.'

    #SI DIGITS ES 0 o menor NO TOMAR EN CUENTA
    if digits == "":
        digits = 0
    if str(digits).isnumeric():
        digits = int(digits)
    if digits > 0 and len(phone)!=digits:
        valid = False
        if error:
            error += ' Dato phone no tiene '+str(digits)+' digitos.'
        else:
            error = 'Dato no tiene '+str(digits)+' digitos.'
    
    return valid, error

def validate_data(data, type):

    valid = True
    error = None

    if not data:
        valid = False
        error = 'Dato vacio.'

        return valid, error
    
    if type in ['int','numero', 'number', 'integer', 'entero']:

        data = data.replace(',','').replace('.','')

        if not data.isnumeric():
            valid = False
            error = 'Dato no es numerico.'

    if type in ['bool', 'boolean', 'booleano', 'boleano']:
        data = data.lower()
        if not data in ['true','false','verdadero','cierto','falso','0','1']:
            valid = False
            error = 'Dato no es un boleano.'

    if type in ['date', 'fecha']:
        
        formatos = ['%d/%m/%Y', '%d/%m/%Y', '%m/%d/%Y', '%m/%d/%Y',
                    '%d-%m-%y', '%d-%m-%Y', '%m-%d-%y', '%m-%d-%Y',
                    '%d %m %y', '%d %m %Y', '%m %d %y', '%m %d %Y']
        fecha_valida = False

        for format in formatos:
            try:
                fecha = time.strptime(data, format)
                fecha = True
                fecha_valida = True
            except:
                pass

        if not fecha_valida:
            valid = False
            error = 'Dato no tiene formato date/fecha.'


    if type in ['datetime', 'time', 'hora']:
        try:
            fecha = datetime.strptime(data, "%Y-%m-%d %H:%M:%S")
        except:
            valid = False
            error = 'Dato no tiene formato de datetime yyyy-mm-dd hh:mm:ss.'

    return valid, error
            
                    



            

    
    

