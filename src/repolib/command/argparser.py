#!/usr/bin/python3

"""
Copyright (c) 2020, Ian Santopietro
All rights reserved.

This file is part of RepoLib.

RepoLib is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

RepoLib is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with RepoLib.  If not, see <https://www.gnu.org/licenses/>.

Module for getting an argparser. Used by apt-manage
"""

import argparse
import inspect

from repolib import command as cmd

from .. import __version__

def get_argparser():
    """ Get an argument parser with our arguments.

    Returns:
        An argparse.ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        prog='apt-manage',
        description='Manage software sources and repositories',
        epilog='apt-manage version: {}'.format(__version__.__version__)
    )

    parser.add_argument(
        '-b',
        '--debug',
        action='count',
        help=argparse.SUPPRESS
    )

    subparsers = parser.add_subparsers(
        help='...',
        dest='action',
        metavar='COMMAND'
    )

    subcommands = []
    for i in inspect.getmembers(cmd, inspect.isclass):
        obj = getattr(cmd, i[0])
        subcommands.append(obj)

    for i in subcommands:
        i.init_options(subparsers)

    return parser
