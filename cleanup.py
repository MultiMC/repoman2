# The "cleanup" command removes all versions older than a certain ID from a channel.

import os, re

import repo
from command import command, Argument, with_channel, with_collection

from storage import FileStorage


@command('mod-urls',
         Argument('match', help='regex pattern to replace'),
         Argument('replace', help='string to replace the pattern with'),
         Argument('--commit', action='store_true', help='if not given, changes are only simulated'),
         description='Perform a regex replace on all of a repo\'s URLs',
)
@with_collection
def mod_urls(collection, match, replace, commit, **kwargs):
    storage = collection.storage


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
         description='Removes versions in the given channel whose ID is less than the given value.',
)
@with_channel
def delete_old(channel, collection, older_than, **kwargs):
    storage = collection.storage
    
    pass
