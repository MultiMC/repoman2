# This file contains functions for dealing with repositories.

import os, json, hashlib

from repoman.backend import Backend
from repoman.storage import FileStorage


class Collection(object):
    """
    Class for managing GoUpdate collections.

    Contains information about the collection's path, base URL, file storage
    URL, etc.
    """
    @classmethod
    def load(cls, backend, path):
        """
        Loads a collection from a folder with a collection.json config file.
        """
        obj = backend.read_json(os.path.join(path, 'config.json'))
        # Base URL for all of the version metadata
        base_url = obj['base_url']
        # Base URL for file storage
        storage_url = obj['storage_url']
        # File storage path (relative to the collection's folder)
        storage_path = obj['storage_path']
        storage = FileStorage(backend, storage_path, storage_url)

        return cls(backend, path, base_url, storage)

    def save(self):
        obj = dict(
            base_url = self.url,
            storage_url = self.storage.url,
            storage_path = self.storage.path,
        )
        self.backend.write_json(obj, self.get_config_path())

    def __init__(self, backend, path, url, storage):
        """
        Constructs and loads the collection.
        """
        self.backend = backend
        self.path = path
        self.url = url
        self.storage = storage
        self.platforms = {}

    def get_platform(self, name):
        """
        Finds a platform in the collection with the given name.

        Returns `None` if no such platform exists.
        """
        if name in self.platforms:
            return name
        else:
            try:
                p = self.platforms['name'] = Platform.load(self, name)
                return p
            except IOError as e:
                print('Failed loading platform: {0}'.format(str(e)))
                return None

    def new_platform(self, id):
        """
        Creates a new platform within the collection. Does not save the platform
        to disk. To save the platform, call `platform.save()`.
        """
        p = Platform(self, id, [])
        self.platforms[id] = p
        return p

    def list_platforms(self):
        dirs = self.backend.list_dir(self.path, type='dirs')
        for id in dirs:
            yield self.get_platform(id)

    def all_versions_where(self, pred):
        """
        A generator which lists of every single version whose ID and name match
        the given predicate.

        The predicate takes a tuple with the version ID and name and returns
        true or false indicating whether the version should be listed.

        This will be horribly slow on non-disk backends like S3.
        """
        for p in self.list_platforms():
            for ch in p.channels:
                for vsn in ch.all_versions_where(pred):
                    yield vsn

    def all_latest_versions(self):
        """
        A generator which lists latest versions from the collection.
        """
        for p in self.list_platforms():
            for ch in p.channels:
                vsn = ch.get_latest_vsn()
                yield vsn

    def get_config_path(self):
        return os.path.join(self.path, 'config.json')



class Platform(object):
    @classmethod
    def load(cls, col, name):
        """
        Loads a platform directory and all of its channels.
        """
        b = col.backend
        path = os.path.join(col.path, name)
        obj = b.read_json(os.path.join(path, 'channels.json'))
        if obj['format_version'] != 0:
            raise 'Format version mismatch.'

        channels = []
        chan_objs = obj['channels']
        for chan_obj in chan_objs:
            try:
                channels.append(Channel.load(b, path, chan_obj))
            except Exception as e:
                print('Failed to load channel "{0}" from platform "{1}": {2}'
                      .format(chan_obj['id'], path, str(e)))
        return cls(col, name, channels)

    def save(self):
        chan_objs = []
        print('Saving platform info for "{0}".'.format(self.name))
        self.backend.write_json(dict(
            format_version = 0,
            channels = [chan.todict() for chan in self.channels]
        ), self.channels_file_path())

    def __init__(self, col, name, channels):
        self.collection = col
        self.backend = col.backend
        self.collection = col
        self.path = os.path.join(col.path, name)
        self.name = name
        self.channels = channels

    def get_channel(self, id):
        """
        Returns a channel with the given ID, creating it if it doesn't exist.

        If the channel is created, `save()` will be called automatically. The
        created channel's name will be the same as its ID, though this can be
        changed manually if necessary. The channel's description will be empty
        and the URL will be determined automatically.
        """
        for ch in self.channels:
            if ch.id == id:
                return ch
        return self.new_channel(id)

    def new_channel(self, id, name=None, desc=''):
        if name == None: name = id
        chan_url = self.collection.url + self.name + '/' + id + '/'
        chan_path = os.path.join(self.path, id)
        chan = Channel(self.backend, id, name, desc, chan_url, chan_path, [])
        self.channels.append(chan)
        self.save()
        return chan

    def channels_file_path(self):
        return os.path.join(self.path, 'channels.json')



class Channel(object):
    @classmethod
    def load(cls, backend, path, obj):
        """
        Loads a channel from the given platform directory based on info in the
        given dict, which should be loaded from the platform's `channels.json`
        file.
        """
        b = backend
        id = obj['id']
        name = obj['name']
        desc = obj['description']
        url = obj['url']
        path = os.path.join(path, id)
        
        # Load the index.json file.
        idx = b.read_json(os.path.join(path, 'index.json'))
        if idx['ApiVersion'] != 0:
            return None
        
        versions = []
        for vsn_obj in idx['Versions']:
            # TODO: Maybe check if the version file exists?
            versions.append(dict(
                id=vsn_obj['Id'],
                name=vsn_obj['Name'],
            ))

        return cls(b, id, name, desc, url, path, versions)

    def save_index(self):
        """
        Saves the channel's index file.
        """
        vsn_objs = [dict(Id = v['id'], Name = v['name']) for v in self.versions]
        self.backend.write_json(dict(
            Versions = vsn_objs,
            Channels = [], # This is unused.
            ApiVersion = 0,
        ), self.index_path())

    def todict(self):
        return dict(
            id = self.id,
            name = self.name,
            description = self.desc,
            url = self.url
        )

    def __init__(self, backend, id, name, desc, url, path, versions):
        self.backend = backend
        self.id = id
        self.name = name
        self.desc = desc
        self.url = url
        self.path = path
        self.versions = versions
        self.loaded_vsns = dict()

    def get_version(self, id):
        """
        Loads full version info for the version with the given ID.
        """
        if id in self.loaded_vsns:
            return self.loaded_vsns[id]
        for v in self.versions:
            if v['id'] == id:
                vsn = Version.load(self.backend, self.path, v['id'], v['name'])
                self.loaded_vsns[v['id']] = vsn
                return vsn

    def add_version(self, id, name, files):
        """
        Adds a new version. Saves both the version and the channel's JSON files
        and returns the added version.
        """
        v = Version(self.backend, self.path, id, name, files)
        v.save()
        self.versions.append(dict(id=id, name=name))
        self.save_index()
        return v

    def delete_version(self):
        """
        Deletes the version with the given ID.

        Does not remove the version's files.
        """
        pass

    def get_latest_vsn(self):
        """Gets the channel's newest version."""
        # The last version in the list should be the newest one.
        if len(self.versions) > 0:
            v = sorted(self.versions, key=lambda v: int(v['id']))[len(self.versions)-1]
            return self.get_version(v['id'])
        else: return None

    def all_versions_where(self, pred):
        """
        A generator which lists of every single version whose ID and name match
        the given predicate.
        
        The predicate takes a tuple with the version ID and name and returns
        true or false indicating whether the version should be listed.

        This will be horribly slow on non-disk backends like S3.
        """
        for v in self.versions:
            if pred(v['id'], v['name']):
                yield self.get_version(v['id'])

    def index_path(self):
        return os.path.join(self.path, 'index.json')



class Version(object):
    """
    Class for holding information about versions.
    """
    
    @classmethod
    def load(cls, backend, chan_dir, id, name):
        # print('Loading version "{0}" ({1}).'.format(name, id))
        b = backend
        jsonFilename = os.path.join(chan_dir, str(id) + '.json')
        # print("Reading: " + jsonFilename)
        obj = b.read_json(jsonFilename)
        assert obj['ApiVersion'] == 0
        assert id == obj['Id']
        #assert name == obj['Name']
        files = []
        for file in obj['Files']:
            # We only support the 'http' type anyway, so we'll just load sources
            # as a list of URLs.
            sources = map(lambda src: src['Url'], file['Sources'])
            path = file['Path']
            executable = file['Executable']
            md5 = file['MD5']
            perms = file['Perms']
            files.append(UpdateFile(path, md5, perms, sources, executable))
        return cls(b, chan_dir, id, name, files)

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
        print('Saving version info to {0}.'.format(self.vsn_file_path()))
        self.backend.write_json(obj, self.vsn_file_path())

    def __init__(self, backend, chan_dir, id, name, files):
        self.backend = backend
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
