from starflyer import Module, AttributeMapper
import uuid
import copy

from stores import FilesystemStore

__all__ = ['Uploader', 'upload_module', 'AssetNotFound']


class AssetNotFound(Exception):
    """an asset was not found"""

    def __init__(self, asset_id):
        self.asset_id = asset_id

    def __repr__(self):
        return """<< AssetNotFound: %s >>""" %self.asset_id

class Asset(AttributeMapper):
    """an asset object with access to the file pointer"""

    def __init__(self, default = {}, store = None, *args, **kwargs):
        super(Asset, self).__init__(default = default, *args, **kwargs)
        self._store = store
    
    def get_fp(self):
        """return the filepointer"""
        return self._store.get(self._id)


class Uploader(Module):
    """an uploader for starflyer which allows a user to upload files to the system.

    Files can be stored in various ways via a storage component and can also be post processed
    e.g. to create thumbnails from images or single pages from a PDF.

    Also included is a mongoengine based asset management component which allows you to keep track of
    your assets as otherwise your app needs to do that.

    """

    name = "uploader"

    default_config = {
        'use_uuid'          : True,
        'metadata_db'       : None,
        'store'             : FilesystemStore(),
        'processors'        : {},
    }

    def add(self, 
        fp,
        filename = None,
        content_length = None,
        content_type = "application/octet-stream",
        store_kw = {},
        metadata = {},
        **kw):
        """add a file to the media database

        :param fp: The file pointer of the file to add, should be seeked to 0
        :param content_length: The size of the file to add (optional, will be computed otherwise)
        :param content_type: The media type of the file to add (optional)
        :param store_kw: optional parameters to be passed to the store
        :param **kw: additional parameters stored alongside the file
        :return: A dictionary containing the final filename, content length and type
        """

        if filename is None:
            filename = unicode(uuid.uuid4())

        # we differ between the incoming filename and the internal one for the store.
        if self.config.use_uuid:
            asset_filename = unicode(uuid.uuid4())
        else:
            asset_filename = filename

        # store filepointer via store. we will get some store related data back. 
        # at least filename and content length 
        asset_md = self.config.store.add(fp, filename=asset_filename)

        metadata.update(kw)

        asset = Asset(
            store = self.config.store,
            _id = asset_md.filename,
            store_metadata = asset_md,
            content_type = content_type, 
            content_length = asset_md.content_length,
            metadata = metadata,
        )
        return asset
    
    def get(self, asset_id, md = {}, **kw):
        """return a file based on the asset id. We will return an asset object in this case
        which is basically the metadata but also has access to the filepointer

        If you use some metadata database in this module you only need to pass in the asset id.
        In case you store metadata yourself in your app you might want to pass it in here if
        you want to have it accessble inside the ``Asset`` instance. 

        :param asset_id: The asset id you want to retrieve from the store
        :param metadata: optional metadata in case you have stored it yourself.
        :param **kw: additional metadata 
        :returns: An instance of ``Asset`` which contains all metadata and the filepointer.
        
        """

        md = copy.copy(md)
        md.update(kw)
        md['_id'] = asset_id
        if not self.config.store.exists(asset_id):
            raise AssetNotFound(asset_id)
        if self.config.metadata_db is None:
            return Asset(store = self.config.store, **md)
        else:
            asset = self.config.metadata_db.get(asset_id)
            asset._store = self.config.store
            return asset

    def remove(self, asset_id):
        """remove an asset from the system

        :param asset_id: the asset id of the asset to remove
        """
        if self.config.metadata_db is None:
            self.config.store.remove(asset_id)
        else:
            self.config.metadata_db.remove(asset_id)
            self.config.store.remove(asset_id)

upload_module = Uploader(__name__)
