from bson import ObjectId

def bson_validation(id_mongo):
    if ObjectId.is_valid(id_mongo):
        return id_mongo
    else:
        raise ValueError
