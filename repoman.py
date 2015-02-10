#!/bin/python

import os

import repo

from push import push
from create import create
from command import command, with_collection
from backend.disk import DiskBackend

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Manage GoUpdate repositories.')

    parser.add_argument('-c', '--collection', type=str, default=os.getcwd(),
                        dest='collection', help='path to the collection to manage')

    parser.add_argument('-b', '--backend', type=str, default='disk',
                        choices=['disk'], dest='backend_type',
                        help='which storage backend to use')

    subparsers = parser.add_subparsers()

    add_command(subparsers, push)
    add_command(subparsers, create)

    args = parser.parse_args()

    if args.backend_type == 'disk':
        args.backend = DiskBackend(os.getcwd())

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
