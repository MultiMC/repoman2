#!/bin/python

import os

import repo

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Manage GoUpdate repositories.')

    parser.add_argument('--path', type=str, default=os.getcwd(),
                        help='path to the collection to manage')

    subparsers = parser.add_subparsers()

    setup_print_info(subparsers.add_parser("info"))

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
    col = repo.Collection(args.path)
    for plat in col.platforms:
        print('Platform "' + plat.path + '":')
        for chan in plat.channels:
            print('\tChannel "{0}": {1} versions.'.format(chan.name, len(chan.versions)))


if __name__ == '__main__':
    main()
