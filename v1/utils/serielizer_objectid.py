import json
from bson import ObjectId

# Clase para transformar un ObjecteId (pymongo) a un objeto serializable.
class jsonEncode(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)