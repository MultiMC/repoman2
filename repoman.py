#!/bin/python

import os

import repo

from push import push
from command import command, with_collection

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Manage GoUpdate repositories.')

    parser.add_argument('-c', '--collection', type=str, default=os.getcwd(),
                        dest='collection', help='path to the collection to manage')

    subparsers = parser.add_subparsers()

    add_command(subparsers, push)

    args = parser.parse_args()
    try:
        args.command
    except AttributeError:
        parser.print_usage()
        exit(-1)
    args.command(args)


def add_command(subparsers, cmd):
    parser = subparsers.add_parser(cmd.name, description=cmd.desc)
    parser.set_defaults(command=cmd)
    cmd.setup(parser)


if __name__ == '__main__':
    main()
