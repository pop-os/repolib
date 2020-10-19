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

from argparse import SUPPRESS
import sys

from . import command

from ..legacy_deb import LegacyDebSource
from ..source import Source, SourceError
from ..util import get_source_path
from ..system import SystemSource

class Modify(command.Command):
    """ Modify subcommand.

    The modify command will allow making modifications to the specified repository.
    It requires providing a repository to modify.

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
        modify_enable.add_argument(
            '--default-mirror',
            help=SUPPRESS
            #help='Sets the default mirror for the system source.'
        )

        # Name
        parser.add_argument(
            '-n',
            '--name',
            help='Set the repository name to NAME'
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
            help=SUPPRESS
            # help=(
            #     'Add the specified option(s) and value(s) to the repository. '
            #     'Multiple option-value pairs should be separated with commas.'
            # )
        )
        parser.add_argument(
            '--remove-option',
            metavar='OPTION=VALUE[,OPTION=VALUE]',
            help=SUPPRESS
            # help=(
            #     'Remove the specified option(s) and value(s) from the repository. '
            #     'Multiple option-value pairs should be separated with commas.'
            # )
        )

    def __init__(self, log, args, parser):
        super().__init__(log, args, parser)
        self.source = None
        self.count = 0

    def finalize_options(self, args):
        """ Finish setting up our options/arguments."""
        super().finalize_options(args)
        self.repo = ' '.join(args.repository)
        self.enable = args.enable
        self.disable = args.disable

        self.actions = {}

        self.actions['endisable'] = None
        for i in ['enable', 'disable']:
            if getattr(args, i):
                self.actions['endisable'] = i

        for i in [
                'default_mirror',
                'name',
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

        if self.repo == 'system':
            self.source = SystemSource()
        elif full_path.suffix == '.sources':
            self.source = Source(ident=self.repo)
        else:
            self.source = LegacyDebSource(ident=self.repo)

        self.source.load_from_file()
        self.log.debug('Actions taken: \n%s', self.actions)
        self.log.info('Source before:\n%s', self.source.make_source_string())

        for i in self.actions:
            getattr(self, i)(self.actions[i])

        self.log.info('Source after:\n%s', self.source.make_source_string())

        if self.count == 0:
            self.log.error('No changes specified, no actions taken')
            return False

        if not self.debug:
            self.source.save_to_disk()
            return True

        return True

    def default_mirror(self, value):
        """ Set the default mirror if this is the system source."""
        if not value:
            # No value provided, take no action
            return
        self.count += 1

        if self.repo == 'system':
            self.source.default_mirror = value

    def name(self, value):
        """ Set the source name. """
        if not value:
            # No value provided, take no action
            return
        self.count += 1
        self.log.info('Set name: %s', value)

        self.source.name = value

    def endisable(self, value):
        """ Enable or disable the source. """
        if not value:
            # No value provided, take no action
            return
        self.count += 1
        self.log.info('Enable/Disable: %s', value)

        if value == 'disable':
            self.source.enabled = False
            return
        self.source.enabled = True

    def add_uri(self, value):
        """ Add URIs to the source. """
        if not value:
            # No value provided, take no action
            return
        self.count += 1
        self.log.info('Add uris: %s', value)

        for uri in value.split():
            if uri not in self.source.uris:
                try:
                    self.source.uris = self.source.uris + [uri]
                except SourceError:
                    self.log.error('The URI "%s" is malformed', uri)
                    sys.exit(1)
                self.log.debug('Added uri: %s', uri)
    def remove_uri(self, value):
        """ Remove URIs from the source. """
        if not value:
            # No value provided, take no action
            return
        self.count += 1
        self.log.info('Remove uris: %s', value)

        for uri in value.split():
            if uri in self.source.uris:
                uris = self.source.uris
                uris.remove(uri)
                self.source.uris = uris
                self.log.debug('Removed uri %s', uri)
    def add_suite(self, value):
        """ Add suites to the source. """
        if not value:
            # No value provided, take no action
            return
        self.count += 1
        self.log.info('Add suites: %s', value)

        for suite in value.split():
            if suite not in self.source.suites:
                self.source.suites = self.source.suites + [suite]
                self.log.debug('Added suite: %s', suite)

    def remove_suite(self, value):
        """ Remove suites from the source. """
        if not value:
            # No value provided, take no action
            return
        self.count += 1
        self.log.info('Remove suites: %s', value)

        for suite in value.split():
            if suite in self.source.suites:
                suites = self.source.suites
                suites.remove(suite)
                self.source.suites = suites
                self.log.debug('Removed suite %s', suite)

    def add_component(self, value):
        """ Add components to the source. """
        if not value:
            # No value provided, take no action
            return
        self.count += 1
        self.log.info('Add components: %s', value)

        for component in value.split():
            if component not in self.source.components:
                self.source.components = self.source.components + [component]
                self.log.debug('Added component: %s', component)

    def remove_component(self, value):
        """ Remove components from the source. """
        if not value:
            # No value provided, take no action
            return
        self.count += 1
        self.log.info('Remove components: %s', value)

        for component in value.split():
            if component in self.source.components:
                components = self.source.components
                components.remove(component)
                self.source.components = components
                self.log.debug('Removed component %s', component)

    def add_option(self, value):
        """ Add options to the source. """
        if not value:
            # No value provided, take no action
            return
        self.count += 1
        self.log.info('Add options: %s', value)

        for option in value.split():
            if option not in self.source.options:
                self.source.options = self.source.options + [option]
                self.log.debug('Added option: %s', option)

    def remove_option(self, value):
        """ Remove options from the source. """
        if not value:
            # No value provided, take no action
            return
        self.count += 1
        self.log.info('Remove options: %s', value)

        for option in value.split():
            if option in self.source.options:
                options = self.source.options
                options.remove(option)
                self.source.options = options
                self.log.debug('Removed option %s', option)
