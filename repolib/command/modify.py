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

from argparse import SUPPRESS

from .command import Command, RepolibCommandError
from .. import util, system

class Modify(Command):
    """Modify Subcommand
    
    Makes modifications to the specified repository

    Options:
        --enable, -e
        --disable, -d
        --default-mirror
        --name
        --add-suite
        --remove-suite
        --add-component
        --remove-component
        --add-uri
        --remove-uri
    
    Hidden Options
        --add-option
        --remove-option
        --default-mirror
    """

    @classmethod
    def init_options(cls, subparsers):
        """ Sets up this command's options parser"""

        sub = subparsers.add_parser(
            'modify',
            help='Change a configured repository.'
        )
        sub.add_argument(
            'repository',
            nargs='*',
            default=['system'],
            help='The repository to modify. Default is the system repository.'
        )

        modify_enable = sub.add_mutually_exclusive_group(
            required=False
        )
        modify_enable.add_argument(
            '-e',
            '--enable',
            action='store_true',
            help='Enable the repository, if disabled.'
        )
        modify_enable.add_argument(
            '-d',
            '--disable',
            action='store_true',
            help=(
                'Disable the repository, if enabled. The system repository cannot '
                'be disabled.'
            )
        )

        modify_enable.add_argument(
            '--source-enable',
            action='store_true',
            help='Enable source code for the repository, if disabled.'
        )
        modify_enable.add_argument(
            '--source-disable',
            action='store_true',
            help='Disable source code for the repository, if enabled.'
        )

        modify_enable.add_argument(
            '--default-mirror',
            help=SUPPRESS
            #help='Sets the default mirror for the system source.'
        )

        # Name
        sub.add_argument(
            '-n',
            '--name',
            help='Set the repository name to NAME'
        )

        # Suites
        sub.add_argument(
            '--add-suite',
            metavar='SUITE[,SUITE]',
            help=(
                'Add the specified suite(s) to the repository. Multiple '
                'repositories should be separated with commas. NOTE: Legacy deb '
                'repositories may only contain one suite.'
            )
        )
        sub.add_argument(
            '--remove-suite',
            metavar='SUITE[,SUITE]',
            help=(
                'Remove the specified suite(s) from the repository. Multiple '
                'repositories should be separated with commas. NOTE: The last '
                'suite in a repository cannot be removed.'
            )
        )

        # Components
        sub.add_argument(
            '--add-component',
            metavar='COMPONENT[,COMPONENT]',
            help=(
                'Add the specified component(s) to the repository. Multiple '
                'repositories should be separated with commas.'
            )
        )
        sub.add_argument(
            '--remove-component',
            metavar='COMPONENT[,COMPONENT]',
            help=(
                'Remove the specified component(s) from the repository. Multiple '
                'repositories should be separated with commas. NOTE: The last '
                'component in a repository cannot be removed.'
            )
        )

        # URIs
        sub.add_argument(
            '--add-uri',
            metavar='URI[,URI]',
            help=(
                'Add the specified URI(s) to the repository. Multiple '
                'repositories should be separated with commas. NOTE: Legacy deb '
                'repositories may only contain one uri.'
            )
        )
        sub.add_argument(
            '--remove-uri',
            metavar='URI[,URI]',
            help=(
                'Remove the specified URI(s) from the repository. Multiple '
                'repositories should be separated with commas. NOTE: The last '
                'uri in a repository cannot be removed.'
            )
        )

        # Options
        sub.add_argument(
            '--add-option',
            metavar='OPTION=VALUE[,OPTION=VALUE]',
            help=SUPPRESS
        )
        sub.add_argument(
            '--remove-option',
            metavar='OPTION=VALUE[,OPTION=VALUE]',
            help=SUPPRESS
        )
    
    def finalize_options(self, args):
        super().finalize_options(args)
        self.count = 0
        self.repo = ' '.join(args.repository)
        self.enable = args.enable
        self.disable = args.disable
        self.source_enable = args.source_enable
        self.source_disable = args.source_disable

        self.actions:dict = {}

        self.actions['endisable'] = None
        for i in ['enable', 'disable']:
            if getattr(args, i):
                self.actions['endisable'] = i
        
        self.actions['source_endisable'] = None
        for i in ['source_enable', 'source_disable']:
            if getattr(args, i):
                self.actions['source_endisable'] = i
        
        for arg in [
            'default_mirror',
            'name',
            'add_uri',
            'add_suite',
            'add_component',
            'remove_uri',
            'remove_suite',
            'remove_component',
            'add_option',
            'remove_option'
        ]:
            self.actions[arg] = getattr(args, arg)
        
        system.load_all_sources()
    
    def run(self):
        """Run the command"""
        self.log.info('Modifying repository %s', self.repo)
        
        system_source = False
        source = None
        for i in system.sources:
            if i.ident == self.repo:
                source = i
        
        if not source:
            self.log.error(
                'The source %s could not be found. Check the spelling',
                self.repo
            )
            return False
        
        if source.ident == 'system':
            system_source = True
        
        self.log.debug('Actions taken:\n%s', self.actions)
        self.log.debug('Source before:\n%s', source)

        for action in self.actions:
            getattr(self, action)(self.actions[action])
        
        self.log.debug('Source after: \n%s', source)

        if self.count == 0:
            self.log.warning('No changes specified, no actions taken')
            return False
        else:
            source.file.save()
            return True
        