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

Module for adding repos to the system in CLI applications.
"""

import os

from ..deb import DebLine
from ..legacy_deb import LegacyDebSource
from ..ppa import PPALine
from ..util import DISTRO_CODENAME

from . import command

class Add(command.Command):
    """ Add subcommand.

    The add command is used for adding new software sources to the system. It
    requires root.

    Options:
        --disable, -d
        --source-code, -s
        --expand, -e
    """

    @classmethod
    def init_options(cls, subparsers):
        """ Sets up this command's options parser.

        Returns:
            The subparser for this command.
        """
        options = subparsers.add_parser(
            'add',
            help='Add a new repository to the system.'
        )
        options.add_argument(
            'deb_line',
            nargs='*',
            default=['822styledeb'],
            help='The deb line of the repository to add'
        )
        options.add_argument(
            '-d',
            '--disable',
            action='store_true',
            help='Add the repository and then set it to disabled.'
        )
        options.add_argument(
            '-s',
            '--source-code',
            action='store_true',
            help='Also enable source code packages for the repository.'
        )
        options.add_argument(
            '-e',
            '--expand',
            action='store_true',
            help='Display expanded details about the repository before adding it.'
        )

    # pylint: disable=too-few-public-methods
    # Thinking of ways to add more, but otherwise this is just simple.

    def __init__(self, log, args, parser):
        super().__init__(log, args, parser)

        self.verbose = False
        if self.args.debug > 1:
            self.verbose = True

        self.expand = args.expand
        self.source_code = args.source_code
        self.disable = args.disable

    def run(self):
        """ Run the command."""
        # pylint: disable=too-many-branches
        # We just need all these different checks.

        if os.geteuid() != 0:
            self.parser.print_usage()
            self.log.error('You need to root, or use sudo.')
            return False

        debline = ' '.join(self.args.deb_line)
        if self.args.deb_line == '822styledeb':
            self.parser.print_usage()
            self.log.error('A repository is required.')
            return False

        if debline.startswith('http') and len(debline.split()) == 1:
            debline = f'deb {debline} {DISTRO_CODENAME} main'

        new_source = LegacyDebSource()
        if debline.startswith('ppa:'):
            add_source = PPALine(debline, verbose=self.verbose)

        elif debline.startswith('deb'):
            self.expand = False
            add_source = DebLine(debline)

        else:
            self.log.critical(
                'The line "%s" is malformed. Double-check the spelling.',
                debline
            )
            return False

        new_source.name = add_source.name
        new_source.filename = f'{add_source.make_name()}.list'
        new_source.sources.append(add_source)

        if not debline.startswith('deb-src'):
            src_source = add_source.copy()
            src_source.enabled = False
        else:
            src_source = add_source

        src_source.enabled = self.source_code

        if not debline.startswith('deb-src'):
            new_source.sources.append(src_source)
        
        new_source.load_from_sources()
        
        add_source.enabled = True

        if self.disable:
            for repo in new_source.sources:
                repo.enabled = False

        new_source.make_names()
        
        self.log.debug(new_source.name)
        self.log.debug(new_source.filename)

        if self.args.debug > 0:
            self.log.info('Debug mode set, not saving.')
            for src in new_source.sources:
                print(f'{src.dump()}\n')
            self.log.info('Filename to save: %s', new_source.filename)
            print(f'{new_source.make_deblines()}')

        if self.expand:
            print(new_source.sources[0].make_source_string())
            print(f'{add_source.ppa_info["description"]}\n')
            print('Press [ENTER] to contine or Ctrl + C to cancel.')
            input()

        if self.args.debug == 0:
            new_source.save_to_disk()
            return True

        return False
