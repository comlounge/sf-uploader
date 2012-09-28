from mongogogo import *

class AssetSchema(Schema):
    content_type = String()
    content_length = Integer()
    filename = String()


class Asset(Record):
    schema = MetadataSchema()
    schemaless = True

class Assets(Collection):

    data_class = Asset
    
