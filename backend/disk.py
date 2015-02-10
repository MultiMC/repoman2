from backend import Backend

import os, json, hashlib, shutil

class DiskBackend(Backend):
    """
    A storage backend which simply writes files to a folder.
    """
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def subpath(self, path):
        return os.path.join(self.root_dir, path)

    def read_json(self, path):
        """
        Reads a JSON file from the given path.
        """
        with open(self.subpath(path), 'r') as f:
            return json.load(f)

    def write_json(self, obj, path):
        """
        Writes a JSON file to the given path.
        """
        with open(self.subpath(path), 'w') as f:
            json.dump(obj, f)
    
    def list_dir(self, path_, type='all'):
        """
        Lists all of the files in the given directory.
        
        If `type` is 'all', lists both directories and files. If `type` is
        'dirs', lists only directories. If `type` is 'files', lists only files.
        """
        path = self.subpath(path_)
        names = os.listdir(path)
        if type == 'dirs':
            return [n for n in names if os.path.isdir(os.path.join(path, n))]
        elif type == 'files':
            return [n for n in names if os.path.isfile(os.path.join(path, n))]
        else:
            return names

    def upload_file(self, src, dest):
        """
        Uploads a local file from the given `src` path to the given `dest` path
        on the backend.
        """
        shutil.copyfile(src, self.subpath(dest))

    def get_md5(self, path):
        """
        Returns a hex digest of the MD5sum of the file at the given path.
        """
        with open(self.subpath(path), 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
