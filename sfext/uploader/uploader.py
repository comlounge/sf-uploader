from starflyer import Module, AttributeMapper
import uuid
import copy

from stores import FilesystemStore
from db import Asset, Assets
from mongogogo import ObjectNotFound

__all__ = ['Uploader', 'upload_module', 'AssetNotFound']


class AssetNotFound(Exception):
    """an asset was not found"""

    def __init__(self, asset_id):
        self.asset_id = asset_id

    def __repr__(self):
        return """<< AssetNotFound: %s >>""" %self.asset_id

class NoAsset(AttributeMapper):
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

    defaults = {
        'use_uuid'          : True,
        'metadata_db'       : None,
        'store'             : FilesystemStore(),
        'asset'             : Asset,
        'assets'            : None, # if None nothing will be stored but only returned
        'processors'        : {},
        'static_folder'     : 'static/',
        'static_url_path'   : '/static',
    }

    def add(self, 
        fp,
        filename = None,
        content_length = None,
        content_type = "application/octet-stream",
        store_kw = {},
        metadata = {},
        asset_id = None,
        **kw):
        """add a file to the media database

        :param fp: The file pointer of the file to add, should be seeked to 0
        :param filename: The filename to be used for the public. Does not need to correspond to the internal one.
        :param asset_id: The id (string) of the asset to be used in the asset database. This is the "internal" filename.
            In case you don't give one, a UUID will be generated.  
        :param content_length: The size of the file to add (optional, will be computed otherwise)
        :param content_type: The media type of the file to add (optional)
        :param store_kw: optional parameters to be passed to the store
        :param **kw: additional parameters stored alongside the file
        :return: A dictionary containing the final filename, content length and type
        """

        if filename is None:
            filename = unicode(uuid.uuid4())

        if asset_id is None:
            asset_id = unicode(uuid.uuid4())

        # store filepointer via store. we will get some store related data back. 
        # at least filename and content length 
        asset_md = self.config.store.add(fp, asset_id=asset_id, filename = filename)

        metadata.update(kw)

        asset = Asset(
            _id = asset_id,
            filename = filename,
            content_type = content_type, 
            content_length = asset_md.content_length,
            store_metadata = asset_md,
            metadata = metadata,
        )
        asset.store = self.config.store
        if self.config.assets is not None:
            asset = self.config.assets.save(asset)
        return asset
    
    def get(self, asset_id, md = {}, **kw):
        """retrieves a file from the store.

        In case you use the asset database you can simply give the asset id. Alternatively you
        can use the filename to directly access the underlying store. You need to give one
        though otherwise None will be returned.
        
        :param asset_id: The internal asset id you want to retrieve from the store
        :param metadata: optional metadata in case you have stored it yourself.
        :param **kw: additional metadata 
        :returns: An instance of ``Asset`` which contains all metadata and the filepointer.
        
        """

        if self.config.assets is not None:
            try:
                asset = self.config.assets.get(asset_id)
            except ObjectNotFound:
                raise AssetNotFound(asset_id)
            filename = asset.filename
        else: 
            md = copy.copy(md)
            md.update(kw)
            asset = Asset(_id = asset_id, **md)

        asset.store = self.config.store

        if not self.config.store.exists(asset_id):
            raise AssetNotFound(asset_id)
        return asset

    def remove(self, asset_id):
        """remove an asset from the system

        :param asset_id: the asset id of the asset to remove
        """
        if self.config.assets is None:
            self.config.store.remove(asset_id)
        else:
            self.config.assets.remove(asset_id)
            self.config.store.remove(asset_id)

upload_module = Uploader(__name__)
