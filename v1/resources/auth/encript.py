A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890@!$/{}()*+%&-_.:;<>|?=#"

#Funcion de encriptado
#C es la clave
def encriptar(mensaje , c):
    x = ""
    p = 0
    for char in mensaje:
        if char is " ":
            x += char
        else:
            i = p % len(c)  #posicion en la clave
            x += A[int((A.find(char) + int(A.find(c))) % len(A))]
            p += 1
    return x


def decrypt(mensaje , c):
    x = ""
    p = 0
    for char in mensaje:
        if char is " ":
            x += char
        else:
            i = p % len(c)  # posicion en la clave
            x += A[int((A.find(char) - int(A.find(c))) % len(A))]
            p += 1
    return x

#print(encriptar("xentric","xentricpasswordvalidator"))