# Module with useful tools for defining subcommands.

import repo


class Command(object):
    """
    Class which wraps a function and turns it into a subcommand.

    Contains functions for setting up the command's arguments and stuff.
    """
    def __init__(self, name, func, setup_func):
        self.name = name
        self.func = func
        self.setup_func = setup_func

    def __call__(self, args):
        self.func(**vars(args))

    def setup(self, parser):
        self.setup_func(parser)


def command(name, setup_func):
    """
    Decorator which takes a name and a function which should set up a command's
    parser as an argument. The decorator then creates a function to execute the
    command.
    """
    # Hacky bullshit because Python decorator arguments are silly.
    # It might be better to just throw this out. Not sure.
    def newfunc(func):
        return Command(name, func, setup_func)
    return newfunc


def with_collection(func):
    """
    Creates a command which operates on a collection by taking the contents of a
    `collection` keyword argument as a path to a collection and loading the
    collection at that path. The `collection` argument's value will be replaced
    with the loaded collection object.
    """
    # TODO: Error handling.
    def newfunc(*args, collection, **kwargs):
        col = repo.Collection.load(collection)
        return func(*args, collection = col, **kwargs)
    return newfunc

def with_platform(func):
    """
    Like `with_collection`, but loads a platform as well.
    """
    @with_collection
    def newfunc(*args, collection, platform, **kwargs):
        plat = collection.get_platform(platform)
        return func(*args, collection = collection, platform = plat, **kwargs)
    return newfunc

def with_channel(func):
    """
    Like `with_collection`, but loads a channel as well.
    """
    @with_platform
    def newfunc(*args, platform, channel, **kwargs):
        chan = platform.get_channel(channel)
        return func(*args, platform = platform, channel = chan, **kwargs)
    return newfunc
