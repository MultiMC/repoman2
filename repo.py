# This file contains functions for dealing with repositories.

import os, json

class Collection(object):
    def __init__(self, dir):
        """
        Constructs and loads the collection.
        """
        self.dir = dir
        self.platforms = []
        self.load()

    def load(self):
        """
        Loads information about the collection.
        This will scan all directories in the collection for platforms.
        """
        items = filter(os.path.isdir,
                       map(lambda name: os.path.join(self.dir, name),
                           os.listdir(self.dir)))
        for path in items:
            try:
                self.platforms.append(Platform.load(path))
            except:
                print('Failed to load platform "{0}".'.format(path))


class Platform(object):
    @classmethod
    def load(cls, dir):
        """
        Loads a platform directory and all of its channels.
        """
        obj = read_json(os.path.join(dir, 'channels.json'))
        if obj['format_version'] != 0:
            raise 'Format version mismatch.'

        channels = []
        chan_objs = obj['channels']
        for chan_obj in chan_objs:
            try:
                channels.append(Channel.load(dir, chan_obj))
            except:
                print('Failed to load channel "{0}" from platform "{1}".'
                      .format(chan_obj['id'], path))
        return cls(dir, channels)

    def __init__(self, path, channels):
        self.path = path
        self.channels = channels



class Channel(object):
    @classmethod
    def load(cls, dir, obj):
        """
        Loads a channel from the given platform directory based on info in the
        given dict, which should be loaded from the platform's `channels.json`
        file.
        """
        id = obj['id']
        name = obj['name']
        desc = obj['description']
        url = obj['url']
        path = os.path.join(dir, id)
        
        # Load the index.json file.
        idx = read_json(os.path.join(path, 'index.json'))
        if idx['ApiVersion'] != 0:
            return None
        
        versions = []
        for vsn_obj in idx['Versions']:
            # TODO: Maybe check if the version file exists?
            versions.append(Version(path, vsn_obj['Id'], vsn_obj['Name']))

        return cls(id, name, desc, url, path, versions)


    def __init__(self, id, name, desc, url, path, versions):
        self.id = id
        self.name = name
        self.desc = desc
        self.url = url
        self.path = path
        self.versions = versions



class Version(object):
    """
    Class for holding information about versions.

    Version information is loaded lazily. That is, version files are not
    actually read until necessary.
    """
    def __init__(self, chan_dir, id, name):
        self.chan_dir = chan_dir
        self.id = id
        self.name = name
        # True if the version file has been loaded.
        self.loaded = False


def read_json(path):
    with open(path) as f:
        return json.load(f)
