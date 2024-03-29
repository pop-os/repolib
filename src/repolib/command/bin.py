#!/usr/bin/python3

"""
Copyright (c) 2019-2023, Ian Santopietro
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
"""

import argparse
import logging
import os
import subprocess
import sys

import repolib 
from repolib import command

system_codename = repolib.util.DISTRO_CODENAME

system_components = [
    'main',
    'universe',
    'multiverse',
    'restricted'
]

system_suites = [
    system_codename,
    f'{system_codename}-updates',
    f'{system_codename}-security',
    f'{system_codename}-backports',
    f'{system_codename}-proposed',
    'updates',
    'security',
    'backports',
    'proposed',
]

def apt_manage():
    """ Main function for apt-manage."""
    # Set up Argument Parsing.
    parser = repolib.command.parser

    # Parse options
    args = parser.parse_args()

    if not args.debug:
        args.debug = 0

    if args.debug > 2:
        args.debug = 2

    verbosity = {
        0 : logging.WARN,
        1 : logging.INFO,
        2 : logging.DEBUG
    }

    log = logging.getLogger('apt-manage')
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(name)s: %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(verbosity[args.debug])
    log.debug('Logging set up!')
    repolib.set_logging_level(args.debug)

    if not args.action:
        args = parser.parse_args(sys.argv[1:] + ['list'])
    
    log.debug('Arguments passed: %s', str(args))
    log.debug('Got command: %s', args.action)

    subcommand = args.action.capitalize()

    command = getattr(repolib.command, subcommand)(log, args, parser)
    result = command.run()
    if not result:
        sys.exit(1)

def add_apt_repository():
    parser = aar_get_args()
    args = parser.parse_args()

    command = ['apt-manage']

    if args.debug:
        command.append('-bb')

    sourceline = args.sourceline
    run = True
    remove = False

    if sourceline in system_components:
        command.append('modify')
        command.append('system')
        if not args.remove:
            command.append('--add-component')
        else:
            command.append('--remove-component')

    elif sourceline in system_suites:
        command.append('modify')
        command.append('system')
        if not args.remove:
            command.append('--add-suite')
        else:
            command.append('--remove-suite')

    else:

        if args.source:
            command.append('source')

        elif args.remove:
            remove = True
            command.append('remove')

        else:
            command.append('add')
            if not args.yes:
                command.append('--expand')

    if not remove:
        command.append(sourceline)
    else:
        sources = repolib.get_all_sources()
        comp_source = repolib.DebLine(sourceline)
        for source in sources:
            if comp_source.uris[0] in source.uris:
                name = str(source.filename.name)
                name = name.replace(".list", "")
                name = name.replace(".sources", "")
                command.append(name)

    run = True

    if os.geteuid() != 0:
        print('Error: must run as root')
        run = False

    if run:
        subprocess.run(command)

        if not args.noupdate:
            subprocess.run(['apt', 'update'])

    print('NOTE: add-apt-repository is deprecated in Pop!_OS. Use this instead:')
    print_command = command.copy()
    if '--expand' in print_command:
        print_command.remove('--expand')
    print(' '.join(print_command))

def aar_get_args():
    parser = argparse.ArgumentParser(
        prog='add-apt-repository',
        description=(
            'add-apt-repository is a script for adding apt sources.list entries.'
            '\nThis command has been deprecated in favor of `apt-manage`. See '
            '`apt-manage --help` for more information.'
        )
    )

    parser.add_argument(
        'sourceline',
        metavar='<sourceline>'
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        '-m',
        '--massive-debug',
        dest='debug',
        action='store_true',
        help='Print a lot of debug information to the command line'
    )

    group.add_argument(
        '-r',
        '--remove',
        action='store_true',
        help='remove repository from sources.list.d directory'
    )

    group.add_argument(
        '-s',
        '--enable-source',
        dest='source',
        action='store_true',
        help='Allow downloading of source packages from the repository'
    )

    parser.add_argument(
        '-y', 
        '--yes',
        action='store_true',
        help='Assum yes to all queries'
    )

    parser.add_argument(
        '-n',
        '--no-update',
        dest='noupdate',
        action='store_true',
        help='Do not update package cache after adding'
    )

    parser.add_argument(
        '-u',
        '--update',
        action='store_true',
        help='Update package cache after adding (legacy option)'
    )

    parser.add_argument(
        '-k',
        '--keyserver',
        metavar='KEYSERVER',
        help='Legacy option, unused.'
    )

    return parser
