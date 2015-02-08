# The "push" command pushes a new version to a particular channel.

import os, stat

import repo

from storage import FileStorage, md5_dir

def setup_cmd(parser):
    parser.add_argument("platform")
    parser.add_argument("channel")
    parser.add_argument("vsn_id")
    parser.add_argument("vsn_name")
    parser.add_argument("vsn_path")
    parser.set_defaults(func=cmd_push)

def cmd_push(args):
    chan = repo.Collection(args.collection).get_platform(args.platform).get_channel(args.channel)
    storage = FileStorage(args.storage)
    
    # Create a new version.
    vsn = new_version(chan, args.vsn_id, args.vsn_name, args.vsn_path, storage)
    vsn.save()
    pass



def new_version(chan, id, name, path, storage):
    """
    Pushes a new version to the given channel from the files at the given path.
    `path` is the path to the files for the new version.
    `storage` is the collection's file storage object.
    """
    last_vsn = chan.get_latest_vsn()

    # Pushing a new version is a somewhat complicated process.
    # We need to be able to make a comparison between the files of the version
    # we're pushing and the files from the version we last pushed in order to
    # see which ones have changed.

    # First, we check the MD5sums of all of the files in our new version.
    new_md5s = md5_dir(path)
    
    # Our goal in is to build a list of `UpdateFile` objects. To do this, we'll
    # go through our list of MD5s, add any new files to storage, and build the
    # list.
    vsn_files = []
    for (md5, path) in new_md5s.items():
        # First, if the file is not already present in storage, we need to add
        # it.
        stored = storage.file_for_md5(md5)
        if stored == None:
            print('Adding new file "{0}".'.format(path))
            stored = storage.add_file(path)
        perms = stat.S_IMODE(os.stat(path).st_mode)
        executable = (perms & stat.S_IXUSR) != 0
        # TODO: Handle slash nonsense better when joining URLs.
        sources = [storage.url + os.path.relpath(stored, storage.path)]
        # Now construct an UpdateFile object for it and add it to the list.
        vsn_files.append(repo.UpdateFile(path, md5, perms, sources, executable));
    
    # Now, we just need to create the new version file.
    return repo.Version(chan.path, id, name, vsn_files)
