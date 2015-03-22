# The "push" command pushes a new version to a particular channel.

import os, stat, hashlib

import repoman.repo as repo
from repoman.command import command, Argument, with_channel

from repoman.storage import FileStorage


@command('push',
         Argument('platform'),
         Argument('channel'),
         Argument('vsn_id'),
         Argument('vsn_name'),
         Argument('vsn_path'),
         description='Push a new version to a particular channel.',
)
@with_channel
def push(channel, collection,
         vsn_id, vsn_name, vsn_path,
         **kwargs):
    """
    Pushes a new version to the given channel from the files at the given path.
    `path` is the path to the files for the new version.
    `storage` is the collection's file storage object.
    """
    storage = collection.storage

    # Pushing a new version is a somewhat complicated process.
    # We need to be able to make a comparison between the files of the version
    # we're pushing and the files from the version we last pushed in order to
    # see which ones have changed.

    os.chdir(vsn_path)

    # First, we check the MD5sums of all of the files in our new version.
    new_md5s = md5_dir('.')

    # Our goal in is to build a list of `UpdateFile` objects. To do this, we'll
    # go through our list of MD5s, add any new files to storage, and build the
    # list.
    vsn_files = []
    for (md5, localPath) in new_md5s.items():
        # First, if the file is not already present in storage, we need to add
        # it.
        remotePath = storage.file_for_md5(md5)
        if remotePath == None:
            print('Adding new file "{0}".'.format(localPath))
            remotePath = storage.add_file(localPath)
        perms = stat.S_IMODE(os.stat(localPath).st_mode)
        executable = (perms & stat.S_IXUSR) != 0
        # TODO: Handle slash nonsense better when joining URLs.
        sources = [storage.url + os.path.relpath(remotePath, storage.path)]
        # Now construct an UpdateFile object for it and add it to the list.
        vsn_files.append(repo.UpdateFile(os.path.normpath(localPath), md5, perms, sources, executable));

    # Now, we just need to create the new version.
    vsn = channel.add_version(vsn_id, vsn_name, vsn_files)


def md5_dir(path):
    """
    Checks the MD5sum of all of the files in a directory and returns a
    dictionary mapping MD5s to filenames.
    """
    md5_map = dict()
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            md5_map[hash_file(file_path).hexdigest()] = file_path
    return md5_map

def hash_file(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read())
