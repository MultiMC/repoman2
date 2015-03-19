# The "push-file" command pushes a single file to a destination in the selected storage.

import os, stat, hashlib

import repoman.repo as repo
from repoman.command import command, Argument, with_channel

from repoman.storage import FileStorage

@command("push-file",
         Argument('repo_path', help=
                  """path in the target storage"""),
         Argument('file_path', help=
                  """full path to the file"""),
         description='Pushes a single file to the remote storage.')
def push_file(backend, repo_path, file_path, **kwargs):
    storage = FileStorage(backend, repo_path, '')
    storage.add_raw_file(file_path)
