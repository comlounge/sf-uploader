from starflyer import AttributeMapper
import shutil
import uuid
import os

class FilesystemStore(object):
    """a filesystem storage"""

    def __init__(self, base_path="/tmp"):
        """initialize the filestore
        
        :param base_path: The path under which the files are supposed to be stored

        TODO:
        - check file existence
        - add path generation e.g. via date and time
        
        """
        self.base_path = base_path

    def add(self, fp, asset_id = None, **kw):
        """add a new file to the store

        :param fp: the file pointer to the file to be stored
        :param asset_id: An optional asset id. If not given, an asset id will be generated. Needs to be a string
        :param kw: optional keyword arguments simply passed back
        :return: A dictionary containing ``asset_id``, the filesystem ``path`` and the ``content_length``
        """
        if asset_id is None:
            asset_id = unicode(uuid.uuid4())

        path = os.path.join(self.base_path, asset_id)
        dirpath = os.path.split(path)[0]
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        dest_fp = open(path, "wb")
        shutil.copyfileobj(fp, dest_fp)
        dest_fp.close()

        content_length = os.path.getsize(path)

        res = AttributeMapper(
            asset_id = asset_id, 
            path = path,
            content_length = content_length
        )
        res.update(kw)
        return res

    def get(self, asset_id):
        """return a file based on the asset_id"""
        path = os.path.join(self.base_path, asset_id)
        return open(path, "rb")

    def remove(self, asset_id):
        """remove a file"""
        path = os.path.join(self.base_path, asset_id)
        if os.path.exists(path):
            os.remove(path) 

    def exists(self, asset_id):
        """check if the asset exists"""
        path = os.path.join(self.base_path, asset_id)
        return os.path.exists(path)

