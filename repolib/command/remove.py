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

from .. import util, system
from .command import Command

class Remove(Command):
    """Remove subcommand
    
    Removes configured sources from the system

    Options:
        --assume-yes, -y
    """

    @classmethod
    def init_options(cls, subparsers):
        """Sets up the argument parser for this command
        
        Returns: argparse.subparser
            This command's subparser
        """

        sub = subparsers.add_parser(
            'remove',
            help='Remove a configured repository'
        )

        sub.add_argument(
            'repository',
            help='The identifier of the repository to remove. See LIST'
        )
        sub.add_argument(
            '-y',
            '--assume-yes',
            action='store_true',
            help='Remove without prompting for confirmation'
        )

    def finalize_options(self, args):
        super().finalize_options(args)
        system.load_all_sources()
        self.source_name = args.repository
        self.assume_yes = args.assume_yes
        self.source = None
    
    def run(self):
        """Run the command"""

        self.log.info('Looking up %s for removal', self.source_name)

        if self.source_name == 'system':
            self.log.error('You cannot remove the system sources')
            return False
        
        if self.source_name not in util.sources:
            self.log.error(
                'Source %s was not found. Double-check the spelling',
                self.source_name
            )
            source_list:list = []
            for source in util.sources:
                source_list.append(source)
            suggested_source:str = self.source_name.replace(':', '-')
            suggested_source = suggested_source.translate(util.CLEAN_CHARS)
            if not suggested_source in source_list:
                return False

            response:str = input(f'Did you mean "{suggested_source}"? (Y/n) ')
            if not response:
                response = 'y'
            if response not in util.true_values:
                return False
            self.source_name = suggested_source

        self.source = util.sources[self.source_name]
        self.key = self.source.key
        self.file = self.source.file
        
        print(f'This will remove the source {self.source_name}')
        print(self.source.ui)
        response:str = 'n'
        if self.assume_yes:
            response = 'y'
        else:
            response = input('Are you sure you want to do this? (y/N) ')
        
        if response in util.true_values:
            self.file.remove_source(self.source_name)
            self.file.save()

            system.load_all_sources()
            for source in util.sources.values():
                self.log.debug('Checking key for %s', source.ident)
                try:
                    if source.key.path == self.key.path:
                        self.log.info('Source key in use with another source')
                        return True
                except AttributeError:
                    pass
            
            self.log.info('No other sources found using key, deleting key')
            if self.key:
                self.key.delete_key()
            return True

        else:
            print('Canceled.')
            return False
