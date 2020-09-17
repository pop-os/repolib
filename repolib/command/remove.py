
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

Command to remove sources from the system.
"""

from pathlib import Path

import dbus

from . import command
from ..util import get_sources_dir, RepoError

class Remove(command.Command):
    # pylint: disable=no-self-use,too-few-public-methods
    # This is a base class for other things to inherit and give other programs
    # a standardized interface for interacting with commands.
    """ Remove subcommand.

    The remove command will remove the selected source. It has no options. Note
    that the system sources cannot be removed. This requires root.
    """

    @classmethod
    def init_options(cls, subparsers):
        """ Sets up this command's options parser.

        Returns:
            The subparser for this command.
        """
        parser_remove = subparsers.add_parser(
            'remove',
            help='Remove a configured repository.'
        )
        parser_remove.add_argument(
            'repository',
            help='The name of the repository to remove. See LIST'
        )

    def __init__(self, log, args, parser):
        super().__init__(log, args, parser)
        self.source = args.repository
        self.sources_dir = get_sources_dir()

    def get_source_path(self):
        """ Tries to get the full path to the source.

        This is necessary because some sources end in .list, others in .sources

        Returns:
            A tuple with the pathlib.Path to the sources, and the pathlib.Path
            to the '.save' file.
        """
        full_name = f'{self.source}.sources'
        full_path = self.sources_dir / full_name
        self.log.debug('Trying to load %s', full_path)
        if full_path.exists():
            return full_path, full_path

        full_name = f'{self.source}.list'
        full_path = self.sources_dir / full_name
        self.log.debug('Trying to load %s', full_path)
        if full_path.exists():
            save_path = Path(f'{full_path}.save')
            return full_path, save_path

        raise RepoError('The path does not exist (checked .sources and .list files.')

    def run(self):
        """ Run the command. """

        if self.source.lower() == 'system':
            self.log.error("You cannot remove the system sources!")
            return False

        try:
            remove_path, remove_path_save = self.get_source_path()
        except RepoError:
            self.log.error(
                'No source %s found on system. Check the spelling.', self.source
            )
            return False

        print(
            f'You are about to remove the sources contained in {remove_path.name}.'
            '\nAre you sure you want to do this?\n'
        )
        response = 'f'
        while response.lower() not in ['y', 'n']:
            response = input(f'Remove {remove_path.name}? (y/N) ')
            if response == '':
                response = 'n'

        if response.lower() == 'y':
            if self.args.debug != 0:
                self.log.info('Simulate: Remove %s', remove_path)
                self.log.info('Simulate: Remove %s', remove_path_save)
            else:
                try:
                    remove_path.unlink()
                    remove_path_save.unlink(missing_ok=True)
                except PermissionError:
                    bus = dbus.SystemBus()
                    privileged_object = bus.get_object('org.pop_os.repolib', '/Repo')
                    privileged_object.delete_source(remove_path.name)
                    privileged_object.exit()

        else:
            print('Canceled.')
            return False

        return True
