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


    # modify subcommand - This will be moved to it's own file.
    # parser_modify = subparsers.add_parser(
    #     'modify',
    #     help='Change a configured repository.'
    # )
    # parser_modify.add_argument(
    #     'repository',
    #     nargs='*',
    #     default=['system'],
    #     help='The repository to modify. Default is the system repository.'
    # )

    # modify_enable = parser_modify.add_mutually_exclusive_group(
    #     required=False
    # )
    # modify_enable.add_argument(
    #     '-e',
    #     '--enable',
    #     action='store_true',
    #     help='Enable the repository, if disabled.'
    # )
    # modify_enable.add_argument(
    #     '-d',
    #     '--disable',
    #     action='store_true',
    #     help=(
    #         'Disable the repository, if enabled. The system repository cannot '
    #         'be disabled.'
    #     )
    # )

    # # Suites
    # parser_modify.add_argument(
    #     '--add-suite',
    #     metavar='SUITE[,SUITE]',
    #     help=(
    #         'Add the specified suite(s) to the repository. Multiple '
    #         'repositories should be separated with commas. NOTE: Legacy deb '
    #         'repositories may only contain one suite.'
    #     )
    # )
    # parser_modify.add_argument(
    #     '--remove-suite',
    #     metavar='SUITE[,SUITE]',
    #     help=(
    #         'Remove the specified suite(s) from the repository. Multiple '
    #         'repositories should be separated with commas. NOTE: The last '
    #         'suite in a repository cannot be removed.'
    #     )
    # )

    # # Components
    # parser_modify.add_argument(
    #     '--add-component',
    #     metavar='COMPONENT[,COMPONENT]',
    #     help=(
    #         'Add the specified component(s) to the repository. Multiple '
    #         'repositories should be separated with commas.'
    #     )
    # )
    # parser_modify.add_argument(
    #     '--remove-component',
    #     metavar='COMPONENT[,COMPONENT]',
    #     help=(
    #         'Remove the specified component(s) from the repository. Multiple '
    #         'repositories should be separated with commas. NOTE: The last '
    #         'component in a repository cannot be removed.'
    #     )
    # )

    # # URIs
    # parser_modify.add_argument(
    #     '--add-uri',
    #     metavar='URI[,URI]',
    #     help=(
    #         'Add the specified URI(s) to the repository. Multiple '
    #         'repositories should be separated with commas. NOTE: Legacy deb '
    #         'repositories may only contain one uri.'
    #     )
    # )
    # parser_modify.add_argument(
    #     '--remove-uri',
    #     metavar='URI[,URI]',
    #     help=(
    #         'Remove the specified URI(s) from the repository. Multiple '
    #         'repositories should be separated with commas. NOTE: The last '
    #         'uri in a repository cannot be removed.'
    #     )
    # )

    # # Options
    # parser_modify.add_argument(
    #     '--add-option',
    #     metavar='OPTION=VALUE[,OPTION=VALUE]',
    #     help=(
    #         'Add the specified option(s) and value(s) to the repository. '
    #         'Multiple option-value pairs should be separated with commas.'
    #     )
    # )
    # parser_modify.add_argument(
    #     '--remove-option',
    #     metavar='OPTION=VALUE[,OPTION=VALUE]',
    #     help=(
    #         'Remove the specified option(s) and value(s) from the repository. '
    #         'Multiple option-value pairs should be separated with commas.'
    #     )
    # )

    return parser
