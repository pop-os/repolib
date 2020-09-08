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

Module for listing repos on the system in CLI applications.
"""

from ..deb import DebLine
from ..legacy_deb import LegacyDebSource
from ..source import Source
from ..util import get_sources_dir, RepoError

from . import command

class List(command.Command):
    """ List subcommand

    The list command lists available software sources as well as details about
    sources. With no further options, it lists all configured sources. With a
    configured source, it lists details about the specified source.

    Options:
        --legacy, -l
        --verbose, v
    """

    @classmethod
    def init_options(cls, subparsers):
        """ Sets up this command's options parser.

        Returns:
            The subparser for this command.
        """
        options = subparsers.add_parser(
            'list',
            help=(
                'List configured repositories. If a repository name is provided, '
                'show details about that repository.'
                )
        )

        options.add_argument(
            'repository',
            nargs='*',
            default=['x-repolib-all-sources'],
            help='The repository to list details about.'
        )
        options.add_argument(
            '-v',
            '--verbose',
            action='store_true',
            help='Display details of all configured repositories.'
        )
        options.add_argument(
            '-l',
            '--legacy',
            action='store_true',
            help='Include listing details about entries configured in sources.list'
        )



    def __init__(self, log, args, parser):
        super().__init__(log, args, parser)
        self.verbose = args.verbose
        self.legacy = args.legacy
        self.source = ' '.join(args.repository)
        self.sources_dir = get_sources_dir()

    def list_all_sources(self):
        """ List all sources on the system, potentially with their info."""
        # pylint: disable=too-many-branches
        # The branches involved control program output. Maybe this can be
        # split into separate methods.
        sources_files = self.sources_dir.glob('*.sources')
        list_files = self.sources_dir.glob('*.list')
        try:
            sources_list_d_file = self.sources_dir.parent / 'sources.list'
        except FileNotFoundError:
            sources_list_d_file = None

        print('Configured sources:')
        for file in sources_files:
            self.log.debug('Found source %s', file.name)
            source = Source(filename=file.name)
            source.load_from_file()

            if self.verbose:
                print(f'{source.make_source_string()}')
            else:
                filename = source.filename.replace(".sources", "")
                print(f'{filename} - {source.name}')

        for file in list_files:
            source = LegacyDebSource(filename=file.name)
            source.load_from_file()

            if len(source.sources) > 0:
                self.log.debug('Found source: %s', file.name)

                if self.verbose:
                    for debsrc in source.sources:
                        print(debsrc.make_source_string())
                else:
                    filename = source.filename.replace('.list', '')
                    print(f'{filename} - {source.name}')

        if sources_list_d_file and self.legacy:
            print('\n Legacy sources.list entries:\n')
            with sources_list_d_file.open(mode='r') as file:
                for line in file:
                    if "cdrom:" in line:
                        line = ''
                    try:
                        source = DebLine(line)
                        print(f'{source.make_debline()}')
                    except RepoError:
                        pass
        return True

    def get_source_path(self):
        """ Tries to get the full path to the source.

        This is necessary because some sources end in .list, others in .sources

        Returns:
            source.Source for the actual full path.
        """
        full_name = f'{self.source}.sources'
        full_path = self.sources_dir / full_name
        self.log.debug('Trying to load %s', full_path)
        if full_path.exists():
            self.log.debug('Path %s exists!', full_path)
            source = Source(filename=full_path.name)
            source.load_from_file()
            return source

        full_name = f'{self.source}.list'
        full_path = self.sources_dir / full_name
        self.log.debug('Trying to load %s', full_path)
        if full_path.exists():
            self.log.debug('Path %s exists!', full_path)
            leg = LegacyDebSource(filename=full_path.name)
            leg.load_from_file()
            return leg

        raise RepoError('The path does not exist (checked .sources and .list files.')

    def run(self):
        """ Run the command. """
        ret = False
        if self.source == 'x-repolib-all-sources':
            ret = self.list_all_sources()

        else:
            try:
                source = self.get_source_path()
            except RepoError:
                self.log.error(
                    "Couldn't find the source file for %s. Check your spelling.",
                    self.source
                )
                return False

            print(f'Details for source {self.source}:\n{source.make_source_string()}')
            ret = True
        return ret
