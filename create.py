# The "create" command creates a new collection.

import os

import repo, storage

from command import command, Argument, with_collection

@command("create",
         Argument('path', help=
                  """path to the collection's root directory"""),
         Argument('url', help=
                  """URL of the collection's root directory"""),
         Argument('storage_path', help=
                  """path to the file storage directory relative to the
                  collection's root directory"""),
         Argument('storage_url', help=
                  """URL of the file storage's root directory"""),
         description='Creates a new collection.')
def create(backend, path, url, storage_path, storage_url, **kwargs):
    if not os.path.isdir(path):
        os.mkdir(path)
    store = storage.FileStorage(backend, storage_path, storage_url)
    collection = repo.Collection(backend, path, url, store)
    collection.save()

@command("add-platform",
         Argument('id', help=
                  """the platform's ID string"""),
         description='Creates a new platform.')
@with_collection
def add_platform(backend, collection, id, **kwargs):
    plat = collection.new_platform(id)
    plat.save()
