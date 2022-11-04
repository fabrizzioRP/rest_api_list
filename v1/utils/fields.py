from mongoengine import DateTimeField, StringField, ReferenceField, ListField, IntField, ObjectIdField
from marshmallow import fields, Schema
from bson import DBRef, ObjectId, SON

"""
serializador de datos relacionados mongoengine para marshmallow

Ejemplo de implementacion:

```python

class DocumentBase(Document):
    name = StringField()


class DocumentChild(Document):
    name = StringField()
    document_base = ReferenceField(DocumentBase)


class DocumentBaseSchema(Schema):
    
    class Meta:
        model = DocumentBase
        fields = ('id', 'name')

class DocumentChildSchema(Schema):
    document_base = MongoRelatedField(schema=DocumentBaseSchema)

    class Meta:
        model = DocumentChild
        fields = ('id', 'name', 'document_base')
```
"""

class MongoRelatedToStr(fields.Str):
    def __init__(self, *args, **kwargs):
        super(MongoRelatedToStr, self).__init__(*args, **kwargs)
        self.related_schema = kwargs.get('schema', None)

    def _serialize(self, value, attr, obj, **kwargs):        
        return str(value.id)

class MongoRelatedField(fields.Field):
    def __init__(self, *args, **kwargs):
        super(MongoRelatedField, self).__init__(*args, **kwargs)
        self.related_schema = kwargs.get('schema', None)

    def _serialize(self, value, attr, obj, **kwargs): 
        try:
            related_id = getattr(value, 'id')
            data = self.related_schema.Meta.model.objects.get(pk=related_id)
        except Exception:
            if isinstance(value, ObjectId):
                    related_id = value
            else:
                related_id = ObjectId(value)
            data = self.related_schema.Meta.model.objects.get(pk=related_id)
        return self.related_schema().dump(data)

