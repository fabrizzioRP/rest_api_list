import csv, codecs, json
from datetime import datetime
from werkzeug.datastructures import FileStorage
from errors import InternalServerError
from bson import DBRef, ObjectId, SON
from mongoengine.errors import NotUniqueError
from mongoengine import DateTimeField, StringField, ReferenceField, ListField, IntField, EmbeddedDocumentListField, EmbeddedDocumentField, BooleanField, DictField, DoesNotExist
from flask_restful import Resource, reqparse
from flask import jsonify, make_response, g
from config import default_datetime_format
from v1.models.auth.authorization import Auth

from v1.utils.marshmallow_mongoengine import ModelSchema, fields
from v1.models.common.models import TrashLog, TrashObject
from v1.models.examples.models import ExampleList, ExampleCampaign
from v1.models.examples.serializer import ExampleCampaignlSchema

def get_fields( model ):
    tmpl = {}
    try:
        tmpl = json.loads( model.objects.filter().order_by('-id').first().to_json() )
    except:
        pass
    keys = []
    for key, value in tmpl.items():
        if key == '_id':
            keys.append('id')
        else:
            keys.append(key)
    return tuple(keys)

class OwnerRelatedField(fields.Str):

    def _serialize(self, value, attr, obj, **kwargs):
        response = {'collection':value.collection, 'id':str(value.id) }
        return response

class MetadataField(fields.Str):

    def _serialize(self, value, attr, obj, **kwargs):
        response = {}
        created = value.get('created', None)
        origin_file = value.get('origin_file', None)
        if created:
            response['created'] = value['created'].strftime(default_datetime_format)
        if origin_file:
            response['origin_file'] = value['origin_file']
        
        return response

class GenericSerializer(ModelSchema):
    id = fields.Str()
    modified_at = fields.DateTime(default_datetime_format)
    created_at = fields.DateTime(default_datetime_format)
    owner = OwnerRelatedField()
    metadata = MetadataField()
    
    class Meta:
        model = ExampleList
        fields = get_fields(ExampleList)

class GenericResource(Resource):
    model = ExampleCampaign
    serializer = ExampleCampaignlSchema
    related_list = ExampleList
    related_index = 'num_ident'
    filters = ['id', 'name']

    def __init__(self, *args, **kwargs):
        super(GenericResource, self).__init__(*args, **kwargs)
        self.parser = reqparse.RequestParser()
        self.model = self.model
        self.serializer = self.serializer
        self.filters = self.filters
        self.related_index = self.related_index

    def get_filter(self, *args, **kwargs):
        for filter in self.filters:
            self.parser.add_argument(filter, type=str, help="Buscar por "+filter+".")

        data = self.parser.parse_args()
        data_filter = {}
        for filter in self.filters:
            if data.get(filter, None):
                data_filter = {key : val for key, val in data.items() if val}

        return data_filter

    @Auth.authenticate
    def get(self, **kwargs):
        if kwargs.get('attach', False):
            return self.attach(method='get', **kwargs)

        data_filter = self.get_filter()

        if self.serializer:
            try:
                schema = self.serializer(many=True)
                queryset = self.model.objects.filter(**data_filter)
                data = schema.dump(queryset, many=True)
                status = 200
            except DoesNotExist as error:
                data = {'error':str(error), 'detail': 'one or more attributes, have relationship inconsistency. Check your data' }
                status = 500
            except Exception as error:
                #data = self.model.objects.filter(**data_filter)
                data = {'error':str(error), 'detail': 'unknow' }
                status = 500

        return data, status

    @Auth.authenticate
    def post(self, **kwargs):
        if kwargs.get('attach', False):
            return self.attach(method='post', **kwargs)
        try:
            required_key = kwargs.get('required_key', 'id')
            inherit_model_required = kwargs.get('inherit_model_required', False)

            if not isinstance(required_key, str) and required_key is not None:
                raise Exception("required_key is not string.")

            if not isinstance(inherit_model_required, bool) and inherit_model_required is not None:
                raise Exception("inherit_model_required is not boolean.")

        except:
            required_key = 'id'
            inherit_model_required = False

        parser = self._set_reqparse(inherit_model_required=True)
        referenced_fields = parser['referenced_fields']
        data = parser['parse_args']

        
        referenced_documents = self._reference_document_manager(parser['referenced_fields'],  data)
        data.update(**referenced_documents)
        instance = self.model(**data)
        try:
            instance.save()
        except NotUniqueError as e:
            mess = str(e)
            response = { 'error': mess }
            return make_response(jsonify(response), 500)
        except Exception as e:
            raise e

        self._embedded_document_manager(parser['embedded_document_fields'], instance, data)
        self._embedded_document_manager(parser['embedded_document_list_fields'], instance, data)

        queryset = self.model.objects.filter(id=instance.id)
        schema = self.serializer(many=True)

        try:
            data = schema.dump(queryset)
        except Exception as e:
            print(e)
            data = queryset
            
        return jsonify(data)

    @Auth.authenticate
    def put(self, **kwargs):
        try:
            required_key = kwargs.get('required_key', 'id')
            inherit_model_required = kwargs.get('inherit_model_required', False)

            if not isinstance(required_key, str) and required_key is not None:
                raise Exception("required_key is not string.")
            if not isinstance(inherit_model_required, bool) and inherit_model_required is not None:
                raise Exception("inherit_model_required is not string.")

        except:
            required_key = 'id'
            inherit_model_required = False

        parser = self._set_reqparse(required_key='id', inherit_model_required=False)
        
        referenced_fields = parser['referenced_fields']
        embedded_document_list_fields = parser['embedded_document_list_fields']
        # document_list_fields = parser['document_list_fields']
        embedded_document_fields = parser['embedded_document_fields']
        data = parser['parse_args']
        _id = data.pop('id')
        data_filter = {'id': _id}
        document = getattr(self.model, 'objects')
        instance = document.get(**data_filter)

        data_put = {}
        for d in data:
            if data.get(d, None):
                data_put = {key : val for key, val in data.items() if val}

        # Reference models
        for key, document in referenced_fields.items():
            if data_put.get(key, False):
                ref_id = data_put[key]
                try:
                    ref_instance = document.objects.get(id=ref_id)
                    data_put[key] = ref_instance.id
                except:
                    data_put[key] = None

        # Embedded 'List/Single' Objects models
        try:
            self._embedded_document_manager(embedded_document_list_fields, instance, data)
        except:
            pass

        try:
            self._embedded_document_manager(embedded_document_fields, instance, data)
        except:
            pass

        if(data_put):
            instance.update(**data_put)
            instance.save()
        
        schema = self.serializer(many=True)
        queryset = self.model.objects.filter(**data_filter)
        
        try:
            data = schema.dump(queryset)
        except Exception as e:
            print(e)
            data = queryset
            
        return jsonify(data)

    @Auth.authenticate
    def delete(self, **kwargs):

        parser = self._set_reqparse(required_key='id', inherit_model_required=False )
        data = parser['parse_args']

        _id = data.pop('id')
        data_filter = {'id': _id}
        document = getattr(self.model, 'objects')

        try:
            instance = document.get(**data_filter)
        except DoesNotExist as e:
            response = {'message': "Does not exist", "filter": data_filter}
            return make_response(jsonify(response), 404)
        except Exception as e:
            raise e

        schema = self.serializer()
        data = schema.dump(instance, many=False)

        deleted_obj = TrashObject(**data)

        deleted_log = TrashLog(
            ref = self.model._collection.name,
            data = deleted_obj
        )
        deleted_log.save()
        instance.delete()

        return jsonify(deleted_log)

    def attach(self, method, *args, **kwargs):

        if method == 'get':
            return self._get_attach(*args, **kwargs)
        
        self.parser.add_argument('id', required=True, type=str, help="Field id is required")
        self.parser.add_argument('file_csv', required=True, type=FileStorage, location='files', help="Field file_csv is required")
        self.parser.add_argument('delimiter', required=True, type=str, help="Field delimiter is required")
        data = self.parser.parse_args()
        delimiter = data.pop('delimiter')
        related_list = getattr(self, 'related_list')
        owner_model = getattr(self, 'model')
        related_index = getattr(self, 'related_index')
        instance = owner_model.objects.get(id=data['id'] )
        input_file_csv = data.get('file_csv', None)
        file_csv = csv.reader(codecs.iterdecode(input_file_csv, 'utf-8'), delimiter=delimiter)
        headers = []
        container = []
        created = 0

        for index, rows in enumerate(file_csv):
            new_obj = {}
            if not index:
                for row in rows:
                    headers.append(row)
            else:
                for idx, header in enumerate(headers):
                    new_obj[header.lower()] = rows[idx]
                ref = DBRef(owner_model._collection.name, instance.id)

                new_obj['metadata'] = {
                    'origin_file': str(input_file_csv.filename),
                    'created': datetime.now()
                }

                new_obj['owner'] = ref
                container.append(new_obj)
        
        for new in container:
            check_filter = {}
            check_filter['metadata__origin_file'] = input_file_csv.filename
            check_filter['owner'] = ref

            if new.get(related_index, None):
                check_filter[related_index] = new.get(related_index)
            
            if not related_list.objects.filter(**check_filter).count():
                created += 1
                related_list(**new).save()

        response = {'message': "attach method", "new data": created}
        return make_response(jsonify(response), 200)

    def _embedded_document_manager(self, embedded_document, instance, data, **kwargs):
        if not embedded_document:
            return None

        embedded_model_field = None

        for key, embedded in embedded_document.items():
            if data.get(key, False):
                embedded_model_field = getattr(instance, key)
                embedded_model_field_type = self.model._fields[key]

                try:
                    if isinstance(embedded_model_field_type, EmbeddedDocumentField):
                        try:
                            new_embedded = embedded_model_field_type.document_type(**data[key])
                            setattr(instance, key, new_embedded)
                            instance.save()

                        except Exception as e:
                            print(datetime.now().strftime(default_datetime_format), e)

                    elif isinstance(embedded_model_field_type, EmbeddedDocumentListField):
                        for d in data[key]:
                            embedded_model_field.delete()
                            embedded_model_field.create(**d)
                    else:
                        raise Exception(type(embedded_document), " arg is not embedded element")
                except Exception as e:
                    element = data.pop(key)
                    raise Exception(e, element)
        return embedded_model_field

    def _reference_document_manager(self, referenced_fields, data, **kwargs):
        referenced_documents = {}

        for key, document in referenced_fields.items():
            if data.get(key, False):
                ref_id = data[key]
                try:
                    ref_instance = document.objects.get(id=ref_id)
                    referenced_documents[key] = ref_instance.id
                    #data[key] = ref_instance.id
                except:
                    data.pop(key)
        return referenced_documents

    def _set_reqparse(self, required_key=None, inherit_model_required=True, **kwargs):
        referenced_fields = {}
        embedded_document_fields = {}
        embedded_document_list_fields = {}
        document_list_fields = {}
        document_dict_fields = {}

        try:
            fields = getattr(self.model, '_fields')
        except Exception as e:
            raise Exception(e, " model not define")

        for key, item in fields.items():
            item_required = item.required
            mess = "is required" if item.required is True else ""

            if not inherit_model_required:
                item_required = False
                mess = ""

            if required_key:
                if key == required_key:
                    # Force required key on resource
                    mess = "is required"
                    self.parser.add_argument(item.name, type=str, required=True, help="Field "+item.name+" "+mess)
                else:
                    # Default required key depending on model
                    self.parser.add_argument(item.name, type=str, required=item_required, help="Field "+item.name+" "+mess)
            else:
                self.parser.add_argument(item.name, type=str, required=item_required, help="Field "+item.name+" "+mess)
                
            if isinstance(item, BooleanField):
                self.parser.remove_argument(item.name)
                self.parser.add_argument(item.name, type=bool, required=item_required, help="Campo "+item.name+".")

            elif isinstance(item, ReferenceField):
                self.parser.remove_argument(item.name)
                referenced_fields[key] = getattr(item, 'document_type')
                self.parser.add_argument(item.name, type=str, required=item_required, help="Campo "+item.name+".")

            elif isinstance(item, EmbeddedDocumentField):
                self.parser.remove_argument(item.name)
                embedded_document_fields[key] = getattr(self.model, key)
                self.parser.add_argument(item.name, type=dict, required=item_required, location='json', help="Campo "+item.name+".")

            elif isinstance(item, ListField):
                self.parser.remove_argument(item.name)
                document_list_fields[key] = getattr(self.model, key)
                self.parser.add_argument(item.name, type=list, required=item_required, location='json', help="Campo "+item.name+".")

            elif isinstance(item, EmbeddedDocumentListField):
                self.parser.remove_argument(item.name)
                embedded_document_list_fields[key] = getattr(self.model, key)
                self.parser.add_argument(item.name, type=list, required=item_required, location='json', help="Campo "+item.name+".")

            elif isinstance(item, DictField):
                self.parser.remove_argument(item.name)
                document_dict_fields[key] = getattr(self.model, key)
                self.parser.add_argument(item.name, type=dict, required=item_required, location='json', help="Campo "+item.name+".")

        result = {
            'parse_args': self.parser.parse_args(),
            'referenced_fields': referenced_fields,
            'embedded_document_list_fields': embedded_document_list_fields,
            'document_list_fields': document_list_fields,
            'embedded_document_fields': embedded_document_fields,
            'document_dict_fields': document_dict_fields
        }

        return result

    def _get_attach(self, *args, **kwargs):
        related_index = getattr(self, 'related_index')
        self.parser.add_argument(related_index, type=str, help="Field "+related_index)
        parser = self._set_reqparse(required_key='id', inherit_model_required=False)
        data = parser['parse_args']
        _id = data.pop('id')
        data_filter = {'id': _id }
        document = getattr(self.model, 'objects')
        instance = document.get(**data_filter)
        related_list = getattr(self, 'related_list')
        owner_model = getattr(self, 'model')
        instance = owner_model.objects.get(id=_id )
        data['owner'] = DBRef(owner_model._collection.name, id=instance.id)
        filter_data = {}

        for d in data:
            if data.get(d, None):
                filter_data = {key : val for key, val in data.items() if val}

        data_response = related_list.objects.filter(**filter_data)
        schema = GenericSerializer(many=True)
        data = schema.dump(data_response, many=True)
        response = jsonify(data)
        
        return response

    
