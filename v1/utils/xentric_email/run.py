import smtplib, ssl, configparser, sys, os, time

entity = sys.argv[1:]

if not entity:
    raise ValueError("Es necesario un argumento para la entidad.")
else:
    entity = entity[0]

from xender import EmailControl
import time

state = True

def service():
    try:
        xender_control = EmailControl(entity)
        xender_control.allocator()
        xender_control.sender()
        time.sleep(60)
    except Exception as error:
        state = False
        raise error

while state == True:
    service()