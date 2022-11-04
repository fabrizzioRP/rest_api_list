from datetime import datetime
from mongoengine import *
from .config import settings
EMAIL_STATUS = ((0, 'in queue'),(1, 'sended'), (2, 'failed'),)

class SourceEmail(Document):

    subject = StringField(db_field='SUBJECT')
    email_from = StringField(db_field='FROM')
    email_to = StringField(db_field='TO')

    body = StringField(db_field='BODY')

    body_phone = IntField(db_field='TELEFONO')
    body_nombre = StringField(db_field='NOMBRE')
    body_email = StringField(db_field='EMAIL')
    sent = IntField(db_field='SENT')
    date = DateTimeField(db_field='DATE')

    meta = {'collection': 'correos'}

class LogEmail(EmbeddedDocument):
    result = StringField()
    status = IntField(choices=EMAIL_STATUS)
    created_at = DateTimeField(default=datetime.now)

class QueueEmail(Document):
    reason = StringField()
    subject = StringField()
    body = StringField()

    retries = IntField(default=0)
    current_status = IntField(choices=EMAIL_STATUS)
    log = ListField(EmbeddedDocumentField(LogEmail))

    created_at = DateTimeField(default=datetime.now)

    meta = { 'indexes': [ { 'fields': ['$reason','current_status'], 'weights': { 'reason': 20 } } ] }
