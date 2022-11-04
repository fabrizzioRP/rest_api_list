
from v1.utils.marshmallow_mongoengine import ModelSchema
from v1.utils.marshmallow_mongoengine import fields
from v1.utils.taskmanager.models import PeriodicTask
from config import default_datetime_format

class PeriodicTaskSchema(ModelSchema):
    expires = fields.DateTime(default_datetime_format)
    start_after = fields.DateTime(default_datetime_format)

    last_run_at = fields.DateTime(default_datetime_format)

    date_changed = fields.DateTime(default_datetime_format)
    date_creation = fields.DateTime(default_datetime_format)

    modified_at = fields.DateTime(default_datetime_format)
    created_at = fields.DateTime(default_datetime_format)

    class Meta:
        model = PeriodicTask
        fields = (
            'interval',
            'queue', 
            'exchange', 
            'routing_key', 
            'soft_time_limit', 
            'expires', 
            'start_after', 
            'enabled', 
            'last_run_at', 
            'total_run_count', 
            'max_run_count', 
            'date_changed', 
            'date_creation', 
            'description', 
            'run_immediately', 
            'modified_at', 
            'created_at'
            )