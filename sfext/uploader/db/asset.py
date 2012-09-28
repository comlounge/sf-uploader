from mongogogo import *

__all__ = ['AssetSchema', 'Asset', 'Assets']

class AssetSchema(Schema):
    content_type = String(default=u"application/octet-stream")
    content_length = Integer(default=0)
    store_metadata = Dict(default={})
    metadata = Dict(default={})
    filename = String(default=u"")

class Asset(Record):
    schema = AssetSchema()
    schemaless = True
    store = None
    _protected = Record._protected+['store']

    def get_fp(self):
        """return the filepointer"""
        return self.store.get(self._id)

class Assets(Collection):

    data_class = Asset
    
