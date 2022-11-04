![image](https://user-images.githubusercontent.com/38040729/135907881-967f7b12-ef8e-491f-8b31-51be1907ba11.png)

# KeycloakAuth
Este decorador permite la autentificacion de usuarios y la separacion de base de datos por cada cliente utilizando la plataforma de keycloak.
## Instalacion en FlaskV1
Para la instalacion de estos decoradores en la estructura que actualmente utiliza xentric deben seguirse los siguientes pasos:
### 1)Incluir KeycloakAuth en el proyecto:
El primer paso es insertar los archivos del decorador en el proyecto en el que lo queremos utilizar, en este caso debe tener la siguiente ruta desde la ruta base del proyecto
  ```/v1/resources/auth/```
  
![image](https://user-images.githubusercontent.com/38040729/135904900-53ce5748-3e90-4c4a-aefd-7e93422ddeda.png)

### 2)Incluir variables de configuracion
El segundo paso a seguir es configurar nuestro decorador, para eso incluiremos las siguientes variables de entorno en el sistema donde ejecutaremos nuestra app (los valores pueden variar):


```



export KeyCloak_ClientID='flask_api'
export KeyCloak_ClientSecret='client secret'
export KeyCloak_UrlToken='https://dockerkeycloak.alloxentric.com/auth/realms/alloxentric/protocol/openid-connect/token'
export KeyCloak_UrlInfo='https://dockerkeycloak.alloxentric.com/auth/realms/alloxentric/protocol/openid-connect/userinfo'

export Bd_Host='bd host'
export Bd_Port='bd puerto'
export Bd_User='bd admin'
export Bd_Pass='bd pass'
export EncriptWord='xentricpasswordvalidator'
``` 
**Una vez realizados estos pasos, los decoradores estaran instalados en nuestro proyecto.**

## Autenticacion y autorizacion
 Una vez los decoradores esten instalados, ya podemos empezar a utilizarlos, para esto seguiremos los siguientes pasos
 #### 1)Nos dirigimos a el archivo routes.py y buscamos el endpoint que deseamos proteger
 
 ![image](https://user-images.githubusercontent.com/38040729/135907010-01b278c9-4b69-4aae-9d42-57db1162bfd5.png)
 
En este caso utilizaremos como ejemplo el endpoint **STT manager**:
En esta seccion debemos indicarle al decorador que recurso sera el que utiliza ese endpoint (al cual se consultara permisos), para esto tenemos 2 opciones:

**Opcion 1: En esta opcion le diremos al decorador que recurso utilizar mediante el atributo ```endpoint``` de flask, para hacer esto pondremos como endpoint el recurso con el siguiente formato ```auth:NombreRecurso``` por ejemplo en este caso ```endpoint="auth:STT" ```**  

![image](https://user-images.githubusercontent.com/38040729/135908483-91738c5b-8a6b-4eb7-bedc-4b206f75a723.png)

** Opcion 2: En el caso de no querer utilizar ```endpoint``` como atributo indicador, se debe dejar este sin el formato anteriormente mencionado y el decorador tomara como nombre del recurso la primera palabra parte de la url dividida por "/", por ejemplo ```/channel/provideer``` tomaria ```channel``` como nombre de recurso

 #### 2)Nos dirigimos a el archivo que contiene el codigo del endpoint e importamos el decorador de autentificacion mediante 
```from v1.resources.auth.authorization import Auth```

#### 3)Una vez hecho esto, nos dirigimos al metodo del endpoint y ponermos el siguiente decorador
```@Auth.authenticate```

Ejemplo: ![image](https://user-images.githubusercontent.com/38040729/135909370-36840fdb-260b-49a6-b7be-0fc8cf3d6f5f.png)

### 4)Una vez hecho esto, nuestro endpoint estara protegido (tambien podremos acceder a la informacion del usuario que se encuentra en la variable de session "user").

## Conexion a la base de datos:
Dentro de las funciones de estos decoradores, existe la funcion de conectarse a la base de datos del cliente que utilizo el endpoint, **(esto solo sirve para bases de datos MongoDB)**, Para utilizar esta funcion se deben seguir los siguientes pasos:

#### 1)Nos dirigimos a el archivo que contiene el codigo del endpoint e importamos el decorador de autentificacion mediante 

```from v1.resources.auth.dbDecorator import dbAccess```

#### 2)Nos dirigimos al metodo del endpoint en el que queremos utilizar la base de datos y ponemos el siguiente decorador:

##### Para MongoEngine: ```@dbAccess.mongoEngineAccess```
##### Para PyMongo: ```@dbAccess.pymongoAccess```

#### 3) Para utilizar la conexion que crea el decorador podemos hacerlo mediante **pymongo** o  **mongoengine**

##### Para Pymongo: Se generara una conexion que quedara guardada en la variable de session "db"
##### Para MongoEngine: Se debe usar el siguiente codigo cuando se quiera utilizar la base datos del usuario:
```python 
with switch_db(ClaseBDaUtilizar,session["db"]) : #se debe tener importadas las sesiones de flask.
    #CODIGO de mongo engine aqui
```
* Ejemplo: *

![image](https://user-images.githubusercontent.com/38040729/135913767-f80f3ca4-115e-4991-824f-ec80e5b19ea0.png)


#### Por cualquier duda comunicarse con Diego Arce.
