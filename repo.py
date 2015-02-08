# This file contains functions for dealing with repositories.

import os, json, hashlib


class Collection(object):
    def __init__(self, path):
        """
        Constructs and loads the collection.
        """
        self.path = path
        self.platforms = []
        self.load()

    def load(self):
        """
        Loads information about the collection.
        This will scan all directories in the collection for platforms.
        """
        dirs = [dir for dir in os.listdir(self.path)
                if os.path.isdir(os.path.join(self.path, dir))]
        for name in dirs:
            try:
                self.platforms.append(Platform.load(name, os.path.join(self.path, name)))
            except:
                print('Failed to load platform "{0}".'.format(name))

    def get_platform(self, name):
        for p in self.platforms:
            if p.name == name:
                return p
        return None



class Platform(object):
    @classmethod
    def load(cls, name, path):
        """
        Loads a platform directory and all of its channels.
        """
        obj = read_json(os.path.join(path, 'channels.json'))
        if obj['format_version'] != 0:
            raise 'Format version mismatch.'

        channels = []
        chan_objs = obj['channels']
        for chan_obj in chan_objs:
            try:
                channels.append(Channel.load(path, chan_obj))
            except Exception as e:
                print('Failed to load channel "{0}" from platform "{1}": {2}'
                      .format(chan_obj['id'], path, str(e)))
        return cls(name, path, channels)

    def __init__(self, name, path, channels):
        self.path = path
        self.name = name
        self.channels = channels

    def get_channel(self, id):
        for ch in self.channels:
            if ch.id == id:
                return ch
        return None



class Channel(object):
    @classmethod
    def load(cls, path, obj):
        """
        Loads a channel from the given platform directory based on info in the
        given dict, which should be loaded from the platform's `channels.json`
        file.
        """
        id = obj['id']
        name = obj['name']
        desc = obj['description']
        url = obj['url']
        path = os.path.join(path, id)
        
        # Load the index.json file.
        idx = read_json(os.path.join(path, 'index.json'))
        if idx['ApiVersion'] != 0:
            return None
        
        versions = []
        for vsn_obj in idx['Versions']:
            # TODO: Maybe check if the version file exists?
            versions.append(Version.load(path, vsn_obj['Id'], vsn_obj['Name']))

        return cls(id, name, desc, url, path, versions)


    def __init__(self, id, name, desc, url, path, versions):
        self.id = id
        self.name = name
        self.desc = desc
        self.url = url
        self.path = path
        self.versions = sorted(versions, key=lambda v: v.id)

    def get_latest_vsn(self):
        """Gets the channel's newest version."""
        # The last version in the list should be the newest one.
        self.versions[len(self.versions)-1]



class Version(object):
    """
    Class for holding information about versions.
    """
    
    @classmethod
    def load(cls, chan_dir, id, name):
        obj = read_json(os.path.join(chan_dir, str(id) + '.json'))
        assert obj['ApiVersion'] == 0
        assert id == obj['Id']
        assert name == obj['Name']
        files = []
        for file in obj['Files']:
            # We only support the 'http' type anyway, so we'll just load sources
            # as a list of URLs.
            sources = map(lambda src: src[0]['Url'], file['Sources'])
            path = file['Path']
            executable = file['Executable']
            md5 = file['MD5']
            perms = file['Perms']
            files.append(UpdateFile(path, md5, perms, sources, executable))
        return cls(chan_dir, id, name, files)

    def save(self):
        file_arr = []
        for file in self.files:
            sources = [{'Url': url, 'SourceType': 'http'} for url in file.sources]
            file_arr.append({
                'Path':       file.path,
                'MD5':        file.md5,
                'Executable': file.executable,
                'Perms':      file.perms,
                'Sources':    sources,
            })
        obj = {
            'ApiVersion': 0,
            'Id':         self.id,
            'Name':       self.name,
            'Files':      file_arr,
        }
        write_json(obj, self.vsn_file_path())

    def __init__(self, chan_dir, id, name, files):
        self.chan_dir = chan_dir
        self.id = id
        self.name = name
        self.files = files

    def vsn_file_path(self):
        return os.path.join(self.chan_dir, str(self.id) + '.json')


class UpdateFile(object):
    def __init__(self, path, md5, perms, sources, executable):
        self.path = path
        self.md5 = md5
        self.perms = perms
        self.sources = sources
        self.executable = executable



def read_json(path):
    with open(path) as f:
        return json.load(f)

def write_json(obj, path):
    with open(path, 'w') as f:
        json.dump(obj, f)
