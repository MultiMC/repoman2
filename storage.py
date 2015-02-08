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
    def __init__(self, path, url):
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
        hash = hash_file(file).hexdigest()
        _, filename = os.path.split(file)
        dest = os.path.join(self.path, '{0}-{1}'.format(hash, filename))
        shutil.copyfile(file, dest)
        return dest

    def load_md5s(self):
        """
        Loads the MD5s of all of the files in storage.
        """
        # TODO: Caching
        self.md5_map = md5_dir(self.path)

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


def md5_dir(path):
    """
    Checks the MD5sum of all of the files in a directory and returns a
    dictionary mapping MD5s to filenames.
    """
    files = [os.path.join(path, file) for file in os.listdir(path)]
    md5_map = dict()
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            md5_map[hash_file(file_path).hexdigest()] = file_path
    return md5_map

def hash_file(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read())
