# The "cleanup" command removes all versions older than a certain ID from a channel.

import os, re

import repoman.repo as repo
from repoman.command import command, Argument, with_channel, with_collection

from repoman.storage import FileStorage


@command('mod-urls',
         Argument('match', help='regex pattern to replace'),
         Argument('replace', help='string to replace the pattern with'),
         Argument('--commit', action='store_true', help='if not given, changes are only simulated'),
         description='Perform a regex replace on all of a repo\'s URLs',
)
@with_collection
def mod_urls(collection, match, replace, commit, **kwargs):
    # For every single version, update file URLs.
    for vsn in collection.all_versions_where(lambda id, name: True):
        for f in vsn.files:
            f.sources = [mod_url(match, replace, url) for url in f.sources]
        if commit: vsn.save()

    # For every platform, update channel URLs.
    for plat in collection.list_platforms():
        for chan in plat.channels:
            chan.url = mod_url(match, replace, chan.url)
        if commit: plat.save()


def mod_url(match, replace, url):
    new = re.sub(match, replace, url)
    print('Changing "{0}" to "{1}.'.format(url, new))
    return new

@command('delete-before',
         Argument('platform'),
         Argument('channel'),
         Argument('older_than', type=int, help="""the minimum version ID to keep"""),
         Argument('--commit', action='store_true', help='if not given, changes are only simulated'),
         description="""
         Removes versions in the given channel whose ID is less than the given value.
         Does not remove the version's files. For that, use the prune command.
         """,
)
@with_channel
def delete_old(channel, collection, older_than, commit, **kwargs):
    for vsn in channel.all_versions_where(lambda id, name: id < older_than):
        print('Delete version "{0}" (version ID {1}).'.format(vsn.name, vsn.id))
        if commit: channel.delete_version(vsn.id)

@command('orphan-files',
         Argument('--delete', action='store_true', help='if given, kill orphans'),
         description="""Removes unused files from storage.""",
)
@with_collection
def orphan_files(collection, delete, **kwargs):
    storage = collection.storage

    # Load a set of all files used.
    files = linked_files(collection)
    # Load a set of all files in storage.
    storage_files = set(storage.get_all_files())
    # Subtract used files.
    to_delete = storage_files - files
    print('Delete: {0}'.format(to_delete))
    print('{0} orphans found.'.format(len(to_delete)))
    if delete:
        for f in to_delete:
            storage.remove_file(f)

@command('obsolete-files',
         Argument('--delete', action='store_true', help='if given, kill obsolete files'),
         description="""Removes obsolete files from storage.""",
)
@with_collection
def obsolete_files(collection, delete, **kwargs):
    storage = collection.storage

    # Load a set of all files used.
    files = latest_files(collection)
    # Load a set of all files in storage.
    storage_files = set(storage.get_all_files())
    # Subtract used files.
    to_delete = storage_files - files
    to_keep = storage_files - to_delete
    print('{0}'.format("\n".join(str(e) for e in to_delete)))
    if delete:
        for f in to_delete:
            storage.remove_file(f)

@command('live-versions',
         description="""Lists versions that are not missing files.""",
)
@with_collection
def live_versions(collection, **kwargs):
    storage = collection.storage
    storage_files = set(storage.get_all_files())
    present_files = set()
    for vsn in collection.all_versions_where(lambda id, name: True):
        files = set()
        for f in vsn.files:
            for src in f.sources:
                files.add(os.path.basename(src))
        dead_files = files - storage_files
        if len(dead_files) == 0:
            # print('{1}/{0}.json'.format(vsn.id, vsn.chan_dir))
            present_files = present_files.union(files)
    print('{0}'.format("\n".join(str(e) for e in present_files)))

def linked_files(collection):
    """
    Returns a set containing the file names of every file linked to by all versions in the given
    collection.
    """
    files = set()
    for vsn in collection.all_versions_where(lambda id, name: True):
        for f in vsn.files:
            for src in f.sources:
                files.add(os.path.basename(src))
    return files

def latest_files(collection):
    """
    Returns a set containing the file names of every file linked to by the latest versions in the given
    collection.
    """
    files = set()
    for vsn in collection.all_latest_versions():
        for f in vsn.files:
            for src in f.sources:
                files.add(os.path.basename(src))
    return files
