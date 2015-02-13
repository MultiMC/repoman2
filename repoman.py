#!/bin/python

import os

import repo

from push import push
from create import create, add_platform
from cleanup import delete_old, mod_urls, orphan_files, dead_versions
from command import command, with_collection
from backend.disk import DiskBackend
from backend.s3 import S3Backend

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Manage GoUpdate repositories.')

    parser.add_argument('-c', '--collection', type=str, default=os.getcwd(),
                        dest='collection', help='path to the collection to manage')

    parser.add_argument('--bucket', type=str, default=None,
                        dest='s3_bucket',
                        help='if specified, stores data in the given S3 bucket instead of on disk')


    subparsers = parser.add_subparsers()

    add_command(subparsers, push)
    add_command(subparsers, create)
    add_command(subparsers, add_platform)

    add_command(subparsers, delete_old)
    add_command(subparsers, mod_urls)
    add_command(subparsers, orphan_files)
    add_command(subparsers, dead_versions)

    args = parser.parse_args()

    if args.s3_bucket != None:
        args.backend = S3Backend(args.s3_bucket)
    else:
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
