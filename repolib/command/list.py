#!/usr/bin/python3

"""
Copyright (c) 2022, Ian Santopietro
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
import textwrap
import traceback

from ..file import SourceFile, SourceFileError
from ..source import Source, SourceError
from .. import RepoError, util, system

from .command import Command, RepolibCommandError

class List(Command):
    """List subcommand
    
    Lists information about currently-configured sources on the system.

    Options:
        --legacy, -l
        --verbose, -v
        --all, -a
        --no-names, -n
        --no-file-names, -f
        --no-indentation
    """

    @classmethod
    def init_options(cls, subparsers):
        """Sets up ths argument parser for this command.
        
        Returns: argparse.subparser:
            This command's subparser
        """

        sub = subparsers.add_parser(
            'list',
            help=(
                'List information for configured repostiories. If a repository '
                'name is provided, details about that repository are printed.'
            )
        )

        sub.add_argument(
            'repository',
            nargs='*',
            default=['x-repolib-all-sources'],
            help='The repository for which to list configuration'
        )
        sub.add_argument(
            '-v',
            '--verbose',
            action='store_true',
            help='Show additional information, if available.'
        )
        sub.add_argument(
            '-a',
            '--all',
            action='store_true',
            help='Display full configuration for all configured repositories.'
        )
        sub.add_argument(
            '-l',
            '--legacy',
            action='store_true',
            help='Include repositories configured in legacy sources.list file.'
        )
        sub.add_argument(
            '-n',
            '--no-names',
            action='store_true',
            dest='skip_names',
            help="Don't print repository names"
        )
        sub.add_argument(
            '-f',
            '--file-names',
            action='store_true',
            dest='print_files',
            help="Don't print names of files"
        )
        sub.add_argument(
            '--no-indentation',
            action='store_true',
            dest='no_indent',
            help=argparse.SUPPRESS
        )
    
    def finalize_options(self, args):
        super().finalize_options(args)
        self.repo = ' '.join(args.repository)
        self.verbose = args.verbose
        self.all = args.all
        self.legacy = args.legacy
        self.skip_names = args.skip_names
        self.print_files = args.print_files
        self.no_indent = args.no_indent
    
    def list_legacy(self, indent) -> None:
        """List the contents of the sources.list file.
        
        Arguments:
            list_file(Path): The sources.list file to try and parse.
            indent(str): An indentation to append to the output
        """
        try:
            sources_list_file = util.SOURCES_DIR.parent / 'sources.list'
        except FileNotFoundError:
            sources_list_file = None

        print('Legacy source.list sources:')
        with open(sources_list_file, mode='r') as file:
            for line in file:
                if 'cdrom' in line:
                    line = ''
                
                try: 
                    source = Source()
                    source.load_from_data([line])
                    print(textwrap.indent(source.ui, indent))
                except SourceError:
                    pass

    def list_all(self):
        """List all sources presently configured in the system
        
        This may include the configuration data for each source as well
        """
        
        indent = '   '
        if self.no_indent:
            indent = ''

        if self.print_files:
            print('Configured source files:')
        
            for file in system.files:
                print(f'{file.path.name}:')

                for source in file.sources:
                    print(textwrap.indent(source.ui, indent))
            
            if self.legacy:
                self.list_legacy(indent)
        
        else:
            print('Configured Sources:')
            for source in system.sources:
                output = system.sources[source]
                print(textwrap.indent(output.ui, indent))
            
            if self.legacy:
                self.list_legacy(indent)
        
        if system.errors:
            print('\n\nThe following files contain formatting errors:')
            for err in system.errors:
                print(err)
            if self.verbose or self.debug:
                print('\nDetails about failing files:')
                for err in system.errors:
                    print(f'{err}:')
                    with open(err.filename) as error_file:
                        print(error_file.read())
                    print('Stack Trace:')
                    traceback.print_tb(system.errors[err].__traceback__)
                    print('\n')
        return True
    
    def run(self):
        """Run the command"""
        system.load_all_sources()
        self.log.debug("Current sources: %s", system.sources)
        ret = False

        if self.all:
            return self.list_all()

        if self.repo == 'x-repolib-all-sources' and not self.all:
            print('Configured Sources:')
            for source in system.sources:
                print(source)
            
            return True
        
        else:
            try:
                output = system.sources[self.source]
                print(f'Details for source {output.ident}:\n{output.ui}')
                return True
            except KeyError:
                self.log.error(
                    "Couldn't find the source file for %s, check the spelling",
                    self.repo
                )
                return False
