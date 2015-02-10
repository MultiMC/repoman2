# Module with useful tools for defining subcommands.

import repo


class Command(object):
    """
    Class which wraps a function and turns it into a subcommand.

    Contains functions for setting up the command's arguments and stuff.
    """
    def __init__(self, func, name, args, description=None):
        self.name = name
        self.desc = description
        self.args = args
        self.func = func

    def __call__(self, args):
        self.func(**vars(args))

    def setup(self, parser):
        """
        Adds arguments for the command to the given argument parser.
        """
        for a in self.args:
            parser.add_argument(*a.args, **a.kwargs)

class Argument(object):
    """
    Class which represents an argument to be added to the argparse parser.
    """
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


def command(name, *args, **kwargs):
    """
    Decorator which takes a name and a function which should set up a command's
    parser as an argument. The decorator then creates a function to execute the
    command.
    """
    # Hacky bullshit because Python decorator arguments are silly.
    # It might be better to just throw this out. Not sure.
    def command_(func):
        return Command(func, name, args, **kwargs)
    return command_


def with_collection(func):
    """
    Creates a command which operates on a collection by taking the contents of a
    `collection` keyword argument as a path to a collection and loading the
    collection at that path. The `collection` argument's value will be replaced
    with the loaded collection object.
    """
    # TODO: Error handling.
    def with_collection_(*args, backend, collection, **kwargs):
        col = repo.Collection.load(backend, collection)
        return func(*args, backend = backend, collection = col, **kwargs)
    return with_collection_

def with_platform(func):
    """
    Like `with_collection`, but loads a platform as well.
    """
    @with_collection
    def with_platform_(*args, collection, platform, **kwargs):
        plat = collection.get_platform(platform)
        return func(*args, collection = collection, platform = plat, **kwargs)
    return with_platform_

def with_channel(func):
    """
    Like `with_collection`, but loads a channel as well.
    """
    @with_platform
    def with_channel_(*args, platform, channel, **kwargs):
        chan = platform.get_channel(channel)
        return func(*args, platform = platform, channel = chan, **kwargs)
    return with_channel_
