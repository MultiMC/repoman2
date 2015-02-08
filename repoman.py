#!/bin/python

import os

import repo
import push

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Manage GoUpdate repositories.')

    parser.add_argument('--collection', type=str, default=os.getcwd(),
                        help='path to the collection to manage')

    parser.add_argument('--storage', type=str, default=os.path.join(os.getcwd(), "files"),
                        help='folder to store update files in')

    subparsers = parser.add_subparsers()

    setup_print_info(subparsers.add_parser("info"))
    push.setup_cmd(subparsers.add_parser("push"))

    args = parser.parse_args()
    try:
        args.func
    except AttributeError:
        parser.print_usage()
        exit(-1)
    args.func(args)


def setup_print_info(parser):
    """Sets up the subparser for the "info" command."""
    parser.set_defaults(func=print_info)

def print_info(args):
    col = repo.Collection(args.collection)
    for plat in col.platforms:
        print('Platform "' + plat.path + '":')
        for chan in plat.channels:
            print('\tChannel "{0}": {1} versions.'.format(chan.name, len(chan.versions)))


if __name__ == '__main__':
    main()
