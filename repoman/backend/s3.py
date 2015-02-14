from repoman.backend import Backend

import os, json, hashlib

import boto
from boto.s3.key import Key

class S3Backend(Backend):
    """
    A storage backend which uses Amazon S3.
    
    AWS IDs are read from environment variables.
    """
    def __init__(self, bucket_name):
        self.conn = boto.connect_s3()
        self.bucket = self.conn.get_bucket(bucket_name)

    def get_contents(self, path):
        """
        Gets the contents of the file at the given path as a string.
        """
        k = Key(self.bucket)
        k.key = path
        return k.get_contents_as_string().decode('utf-8')

    def set_contents(self, string, path):
        """
        Sets the contents of the file at the given path to the given string.
        """
        k = Key(self.bucket)
        k.key = path
        k.set_metadata('Content-Type', 'application/json')
        k.set_contents_from_string(string)

    def read_json(self, path):
        """
        Reads a JSON file from the given path.
        """
        return json.loads(self.get_contents(path))

    def write_json(self, obj, path):
        """
        Writes a JSON file to the given path.
        """
        return self.set_contents(json.dumps(obj), path)
    
    def list_dir(self, path, type='all'):
        """
        Lists all of the files in the given directory non-recursively.
        
        If `type` is 'all', lists both directories and files. If `type` is
        'dirs', lists only directories. If `type` is 'files', lists only files.
        """
        if not type in ['dirs', 'files', 'all']:
            raise ValueError('Invalid list_dir type: {0}'.format(type))

        list = []
        keys = [n.key for n in self.bucket.list(path)]
        if type == 'files' or type == 'all':
            list += [k for k in keys if is_file_key(k)]
        if type == 'dirs' or type == 'all':
            list += key_dirs(path, keys)
        return [path_last_component(p) for p in list]

    def upload_file(self, src, dest):
        """
        Uploads a local file from the given `src` path to the given `dest` path
        on the backend.
        """
        k = Key(self.bucket)
        k.key = dest
        k.set_contents_from_filename(src)

    def delete_file(self, path):
        """
        Uploads a local file from the given `src` path to the given `dest` path
        on the backend.
        """
        k = self.bucket.get_key(path)
        k.delete()

    def get_md5(self, path):
        """
        Returns a hex digest of the MD5sum of the file at the given path.
        """
        k = self.bucket.get_key(path)
        if k == None: return None
        return k.etag.strip('"')


def is_file_key(path):
    """Returns True if the given S3 key is a file."""
    return not path.endswith('/')

def key_dirs(path, keys):
    """Iterates over a list of keys and returns a list of directories."""
    # FIXME: This is CrAzY!
    if path.endswith('/'): path = path[:-1]
    dirset = set()
    for k in keys:
        kp = os.path.dirname(k)
        if os.path.dirname(kp) == path:
            dirset.add(os.path.basename(kp))
    return list(dirset)


def path_last_component(path):
    if path.endswith('/'):
        return os.path.basename(path.strip('/')) + '/'
    else:
        return os.path.basename(path)
