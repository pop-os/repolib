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

Module for modifying repos in CLI applications.
"""

from . import command

from ..legacy_deb import LegacyDebSource
from ..source import Source
from ..util import get_source_path

class Modify(command.Command):
    """ Modify subcommand.

    The modify command will allow making modifications to the specified repository.
    It requires providing a repository to modify.

    Options:
        --enable, -e
        --disable, -d
        --add-suite
        --remove-suite
        --add-component
        --remove-component
        --add-uri
        --remove-uri
        --add-option
        --remove-option
    """

    @classmethod
    def init_options(cls, subparsers):
        """ Sets up this command's options parser."""

        parser = subparsers.add_parser(
            'modify',
            help='Change a configured repository.'
        )
        parser.add_argument(
            'repository',
            nargs='*',
            default=['system'],
            help='The repository to modify. Default is the system repository.'
        )

        modify_enable = parser.add_mutually_exclusive_group(
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

        # Suites
        parser.add_argument(
            '--add-suite',
            metavar='SUITE[,SUITE]',
            help=(
                'Add the specified suite(s) to the repository. Multiple '
                'repositories should be separated with commas. NOTE: Legacy deb '
                'repositories may only contain one suite.'
            )
        )
        parser.add_argument(
            '--remove-suite',
            metavar='SUITE[,SUITE]',
            help=(
                'Remove the specified suite(s) from the repository. Multiple '
                'repositories should be separated with commas. NOTE: The last '
                'suite in a repository cannot be removed.'
            )
        )

        # Components
        parser.add_argument(
            '--add-component',
            metavar='COMPONENT[,COMPONENT]',
            help=(
                'Add the specified component(s) to the repository. Multiple '
                'repositories should be separated with commas.'
            )
        )
        parser.add_argument(
            '--remove-component',
            metavar='COMPONENT[,COMPONENT]',
            help=(
                'Remove the specified component(s) from the repository. Multiple '
                'repositories should be separated with commas. NOTE: The last '
                'component in a repository cannot be removed.'
            )
        )

        # URIs
        parser.add_argument(
            '--add-uri',
            metavar='URI[,URI]',
            help=(
                'Add the specified URI(s) to the repository. Multiple '
                'repositories should be separated with commas. NOTE: Legacy deb '
                'repositories may only contain one uri.'
            )
        )
        parser.add_argument(
            '--remove-uri',
            metavar='URI[,URI]',
            help=(
                'Remove the specified URI(s) from the repository. Multiple '
                'repositories should be separated with commas. NOTE: The last '
                'uri in a repository cannot be removed.'
            )
        )

        # Options
        parser.add_argument(
            '--add-option',
            metavar='OPTION=VALUE[,OPTION=VALUE]',
            help=(
                'Add the specified option(s) and value(s) to the repository. '
                'Multiple option-value pairs should be separated with commas.'
            )
        )
        parser.add_argument(
            '--remove-option',
            metavar='OPTION=VALUE[,OPTION=VALUE]',
            help=(
                'Remove the specified option(s) and value(s) from the repository. '
                'Multiple option-value pairs should be separated with commas.'
            )
        )

    def __init__(self, log, args, parser):
        super().__init__(log, args, parser)
        self.source = None

    def finalize_options(self, args):
        """ Finish setting up our options/arguments."""
        self.repo = ' '.join(args.repository)
        self.enable = args.enable
        self.disable = args.disable

        self.actions = {}

        self.actions['endisable'] = None
        for i in ['enable', 'disable']:
            if getattr(args, i):
                self.actions['endisable'] = i

        for i in [
                'add_uri',
                'remove_uri',
                'add_suite',
                'remove_suite',
                'add_component',
                'remove_component',
                'add_option',
                'remove_option'
        ]:
            self.actions[i] = getattr(args, i)

    def run(self):
        """ Run the command."""
        self.log.debug('Modifying repository %s', self.repo)
        full_path = get_source_path(self.repo, log=self.log)

        if not full_path:
            self.log.error('Could not find source %s', self.repo)
            return False

        if full_path.suffix == '.sources':
            self.source = Source(filename=full_path.name)
        else:
            self.source = LegacyDebSource(filename=full_path.name)

        self.log.debug('Actions taken: \n%s', self.actions)

        for i in self.actions:
            getattr(self, i)(self.actions[i])

        return True

    def endisable(self, value):
        """ Enable or disable the source. """
        self.log.debug('Enable/Disable: %s', value)

    def add_uri(self, value):
        """ Add URIs to the source. """
        self.log.debug('Add uris: %s', value)

    def remove_uri(self, value):
        """ Remove URIs from the source. """
        self.log.debug('Remove uris: %s', value)

    def add_suite(self, value):
        """ Add suites to the source. """
        self.log.debug('Add suites: %s', value)

    def remove_suite(self, value):
        """ Remove suites from the source. """
        self.log.debug('Remove suites: %s', value)

    def add_component(self, value):
        """ Add components to the source. """
        self.log.debug('Add components: %s', value)

    def remove_component(self, value):
        """ Remove components from the source. """
        self.log.debug('Remove components: %s', value)

    def add_option(self, value):
        """ Add options to the source. """
        self.log.debug('Add options: %s', value)

    def remove_option(self, value):
        """ Remove options from the source. """
        self.log.debug('Remove options: %s', value)
