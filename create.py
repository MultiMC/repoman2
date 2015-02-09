# The "create" command creates a new collection.

import os

import repo, storage

from command import command, Argument

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
def create(path, url, storage_path, storage_url, **kwargs):
    if not os.path.isdir(path):
        os.mkdir(path)
    store = storage.FileStorage(storage_path, storage_url)
    collection = repo.Collection(path, url, store)
    collection.save()
