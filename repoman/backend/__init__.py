# This module defines interfaces for the various backends that can be used to
# store version information.

import os

class Backend(object):
    """
    Base class for backend storage implementations.
    """
    def __init__(self):
        pass

    def read_json(self, path):
        """
        Reads a JSON file from the given path.
        """
        raise NotImplementedError()

    def write_json(self, obj, path):
        """
        Writes a JSON file to the given path.
        """
        raise NotImplementedError()

    def list_dir(self, path, type='all'):
        """
        Lists all of the files in the given directory.

        If `type` is 'all', lists both directories and files. If `type` is
        'dirs', lists only directories. If `type` is 'files', lists only files.
        """
        raise NotImplementedError()

    def upload_file(self, src, dest):
        """
        Uploads a local file from the given `src` path to the given `dest` path
        on the backend.
        """
        raise NotImplementedError()

    def delete_file(self, path):
        """
        Deletes the given file.
        """
        raise NotImplementedError()

    def get_md5(self, path):
        """
        Returns a hex digest of the MD5sum of the file at the given path.
        """
        raise NotImplementedError()

    def md5_dir(self, path):
        """
        Checks the MD5sum of all of the files in a directory and returns a
        dictionary mapping MD5s to filenames.

        This function does not recurse into subdirectories.
        """
        files = self.list_dir(path, 'files')
        md5_map = dict()
        for file in files:
            file_path = os.path.join(path, file)
            md5_map[self.get_md5(file_path)] = file_path
        return md5_map

    def sanitize_file_name(self, filename):
        """
        Returns a sanitized version of the filename, suitable for the backend
        """
        raise NotImplementedError()