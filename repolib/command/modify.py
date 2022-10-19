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

        modify_source = sub.add_mutually_exclusive_group(
            required=False
        )

        modify_source.add_argument(
            '--source-enable',
            action='store_true',
            help='Enable source code for the repository, if disabled.'
        )
        modify_source.add_argument(
            '--source-disable',
            action='store_true',
            help='Disable source code for the repository, if enabled.'
        )

        sub.add_argument(
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
        ]:
            self.actions[arg] = getattr(args, arg)
        
        system.load_all_sources()
    
    def run(self):
        """Run the command"""
        self.log.info('Modifying repository %s', self.repo)
        
        self.system_source = False
        try:
            self.source = util.sources[self.repo]
        except KeyError:
            self.log.error(
                'The source %s could not be found. Check the spelling',
                self.repo
            )
            return False
        
        if self.source.ident == 'system':
            self.system_source = True
        
        self.log.debug('Actions to take:\n%s', self.actions)
        self.log.debug('Source before:\n%s', self.source)

        rets = []
        for action in self.actions:
            ret = getattr(self, action)(self.actions[action])
            rets.append(ret)
        
        self.log.debug('Results: %s', rets)
        self.log.debug('Source after: \n%s', self.source)

        if True in rets:
            self.source.file.save()
            return True
        else:
            self.log.warning('No valid changes specified, no actions taken.')
            return False
        
    def default_mirror(self, value:str)  -> bool:
        """Checks if this is the system source, then set the default mirror"""
        if not value:
            return False
        
        if self.system_source:
            self.source['X-Repolib-Default-Mirror'] = value
            return True
        return False

    def name(self, value:str) -> bool:
        """Sets the source name"""
        if not value:
            return False
        
        self.log.info('Setting name for %s to %s', self.repo, value)
        self.source.name = value
        return True
    
    def endisable(self, value:str) -> bool:
        """Enable or disable the source"""
        if not value:
            return False
        
        self.log.info('%sing source %s', value[:-1], self.repo)
        if value == 'disable':
            self.source.enabled = False
            return True

        self.source.enabled = True
        return True
    
    def source_endisable(self, value:str) -> bool:
        """Enable/disable source code for the repo"""
        if not value:
            return False
        
        self.log.info('%sing source code for source %s', value[7:-1], self.repo)
        if value == 'source_disable':
            self.source.sourcecode_enabled = False
            return True
        
        self.source.sourcecode_enabled = True
        return True
    
    def add_uri(self, values:str) -> bool:
        """Adds URIs to the source, if not already present."""
        if not values:
            return False

        self.log.info('Adding URIs: %s', values)
        uris = self.source.uris

        for uri in values.split():
            if not util.url_validator(uri):
                raise RepolibCommandError(
                    f'Cannot add URI {uri} to {self.repo}. The URI is '
                    'malformed'
                )
                
            if uri not in uris:
                uris.append(uri)
                self.log.debug('Added URI %s', uri)

            else:
                self.log.warning(
                    'The URI %s was already present in %s',
                    uri, 
                    self.repo
                )

        if uris != self.source.uris:
            self.source.uris = uris
            return True
        return False
    
    def remove_uri(self, values:str) -> bool:
        """Remove URIs from the soruce, if they are added."""
        if not values:
            return False
        
        self.log.info('Removing URIs %s from source %s', values, self.repo)
        uris = self.source.uris
        self.log.debug('Starting uris: %s', uris)

        for uri in values.split():
            try:
                uris.remove(uri)
                self.log.debug('Removed URI %s', uri)

            except ValueError:
                self.log.warning(
                    'The URI %s was not present in %s', 
                    uri,
                    self.repo
                )
        
        if len(uris) == 0:
            self.log.error(
                'Cannot remove the last URI from %s. If you meant to delete the source, try REMOVE instead.',
                self.repo
            )
            return False
        
        if uris != self.source.uris:
            self.source.uris = uris
            return True
        
        return False
    
    def add_suite(self, values:str) -> bool:
        """Adds a suite to the source"""
        if not values:
            return False

        self.log.info('Adding suites: %s', values)
        suites = self.source.suites

        for suite in values.split():
            if suite not in suites:
                suites.append(suite)
                self.log.debug('Added suite %s', suite)

            else:
                self.log.warning(
                    'The suite %s was already present in %s',
                    suite, 
                    self.repo
                )
        
        if suites != self.source.suites:
            self.source.suites = suites
            return True
        return False
    
    def remove_suite(self, values:str) -> bool:
        """Remove a suite from the source"""
        if not values:
            return False
        
        self.log.info('Removing suites %s from source %s', values, self.repo)
        suites = self.source.suites
        self.log.debug('Starting suites: %s', suites)

        for suite in values.split():
            try:
                suites.remove(suite)
                self.log.debug('Removed suite %s', suite)

            except ValueError:
                self.log.warning(
                    'The suite %s was not present in %s', 
                    suite,
                    self.repo
                )
        
        if len(suites) == 0:
            self.log.error(
                'Cannot remove the last suite from %s. If you meant to delete the source, try REMOVE instead.',
                self.repo
            )
            return False
        
        if suites != self.source.suites:
            self.source.suites = suites
            return True
        
        return False
    
    def add_component(self, values:str) -> bool:
        """Adds components to the source"""
        if not values:
            return False

        self.log.info('Adding components: %s', values)
        components = self.source.components

        for component in values.split():
            if component not in components:
                components.append(component)
                self.log.debug('Added component %s', component)

            else:
                self.log.warning(
                    'The component %s was already present in %s',
                    component, 
                    self.repo
                )
        
        if len(components) > 1:
            if self.source.file.format == util.SourceFormat.LEGACY:
                self.log.warning(
                    'Adding multiple components to a legacy source is not '
                    'supported. Consider converting the source to DEB822 format.'
                )

        if components != self.source.components:
            self.source.components = components
            return True
        return False

    def remove_component(self, values:str) -> bool:
        """Removes components from the source"""
        if not values:
            return False
        
        self.log.info('Removing components %s from source %s', values, self.repo)
        components = self.source.components
        self.log.debug('Starting components: %s', components)

        for component in values.split():
            try:
                components.remove(component)
                self.log.debug('Removed component %s', component)

            except ValueError:
                self.log.warning(
                    'The component %s was not present in %s', 
                    component,
                    self.repo
                )
        
        if len(components) == 0:
            self.log.error(
                'Cannot remove the last component from %s. If you meant to delete the source, try REMOVE instead.',
                self.repo
            )
            return False
        
        if components != self.source.components:
            self.source.components = components
            return True
        
        return False
    
    def add_option(self, values) -> bool:
        """TODO: Support options"""
        raise NotImplementedError(
            'Options have not been implemented in this version of repolib yet. '
            f'Please edit the file {self.source.file.path} manually.'
        )
        
    
    def remove_option(self, values) -> bool:
        """TODO: Support options"""
        raise NotImplementedError(
            'Options have not been implemented in this version of repolib yet. '
            f'Please edit the file {self.source.file.path} manually.'
        )
