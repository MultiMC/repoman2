import os, hashlib, shutil

def md5s_loaded(func):
    """Decorator which automatically calls load_md5s."""
    def newfunc(self, *args, **kwargs):
        if self.md5_map == None:
            self.load_md5s()
        return func(self, *args, **kwargs)
    return newfunc

class FileStorage(object):
    """
    Class for managing a GoUpdate collection's file storage.
    
    This is the central folder where all of the update files themselves are
    stored. This class is used for things such as checking the MD5s of existing
    files and adding new files to storage.
    
    The class also manages a cache of the storage files' MD5s in an `cache.json`
    file inside the storage directory.
    """
    def __init__(self, backend, path, url):
        self.backend = backend
        self.path = path
        self.url = url
        # When this is None, it indicates MD5s haven't been loaded yet.
        self.md5_map = None

    @md5s_loaded
    def add_file(self, file):
        """
        Adds the given file to storage.
        """
        # We need to determine the destination file name. We can do this by
        # prepending the file's hash to the filename.
        hash = hash_file(file)
        _, filename = os.path.split(file)
        dest = os.path.join(self.path, '{0}-{1}'.format(hash, filename))
        self.backend.upload_file(file, dest)
        return dest

    def remove_file(self, filename):
        """
        Deletes the given file.
        """
        self.backend.delete_file(os.path.join(self.path, filename))
        if self.md5_map != None:
            md5_map = dict([(k, v) for k, v in self.md5_map.items if v != path])

    def load_md5s(self):
        """
        Loads the MD5s of all of the files in storage.
        """
        # TODO: Caching
        self.md5_map = self.backend.md5_dir(self.path)

    @md5s_loaded
    def is_md5_present(self, md5):
        """
        Checks if a file with the given MD5 exists.
        """
        return md5 in self.md5_map

    @md5s_loaded
    def file_for_md5(self, md5):
        """
        Returns the filename of the file with the given MD5, or None if no such
        file exists.
        """
        if md5 in self.md5_map:
            return self.md5_map[md5]
        else:
            return None

    def get_all_files(self):
        return [os.path.basename(f) for f in self.backend.list_dir(self.path, 'files')]

def hash_file(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()
