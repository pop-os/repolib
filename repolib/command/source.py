
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

Source Subcommand.
"""

from ..legacy_deb import LegacyDebSource
from ..source import Source as Source_obj
from ..util import get_source_path

from . import command

class Source(command.Command):
    """ Source Subcommand.

    The source command allows enabling or disabling source code in configured
    sources. If a configured source is provided, this command will affect that
    source. If no sources are provided, this command will affect all sources on
    the system. Without options, it will list the status for source
    code packages.

    Options:
        --enable, -e
        --disable, -d
    """

    @classmethod
    def init_options(cls, subparsers):
        """ Sets up this command's options parser.

        Returns:
            The subparser for this command.
        """
        parser_source = subparsers.add_parser(
            'source',
            help='Enable/disable source code packages for repositories'
        )
        parser_source.add_argument(
            'repository',
            nargs='*',
            default=['x-repolib-all-sources'],
            help=(
                'The repository for which to modify source code packages. If not '
                'specified, then attempt to modify for all repositories.'
            )
        )

        source_enable = parser_source.add_mutually_exclusive_group(
            required=True
        )
        source_enable.add_argument(
            '-e',
            '--enable',
            action='store_true',
            dest='source_enable',
            help='Enable source code for the repository'
        )
        source_enable.add_argument(
            '-d',
            '--disable',
            action='store_true',
            dest='source_disable',
            help='Disable source code for the repository'
        )

    def finalize_options(self, args):
        """ Set up options:

        args.repository [str]: The repository to modify
        args.enable | args.disable: whether to enable or disable source code.
        """
        super().finalize_options(args)
        self.repo = ' '.join(args.repository)
        self.enable = True
        if args.source_disable:
            self.enable = False

    def get_sources_files(self):
        """ Gets the current sources files from the system.

        Returns:
            sources_files, list_files, the files ending in .sources, and .list
        """
        sources_files_glob = self.sources_dir.glob('*.sources')
        list_files_glob = self.sources_dir.glob('*.list')
        sources_files = []
        list_files = []

        for file in sources_files_glob:
            self.log.debug('Found source %s', file)
            source = Source_obj(filename=file.name)
            source.load_from_file()
            sources_files.append(source)
        for file in list_files_glob:
            self.log.debug('Found source %s', file)
            source = LegacyDebSource(filename=file.name)
            source.load_from_file()
            list_files.append(source)

        return sources_files, list_files

    def run(self):
        """ Run the command."""
        if self.repo == 'x-repolib-all-sources':
            self.log.debug('Setting for all repos: Source Code: %s', self.enable)
            sources_files, list_files = self.get_sources_files()
            sources_files += list_files

            for repo in sources_files:
                try:
                    set_source_enabled(repo, self.enable)
                    if self.verbose:
                        print(repo.make_source_string())
                    if not self.debug:
                        repo.save_to_disk()
                except command.RepolibCommandError as e:
                    self.log.error(
                        'Could not change source code for %s:\n%s',
                        self.repo,
                        e
                    )

            return True

        self.log.debug('Setting for repo %s: Source Code: %s', self.repo, self.enable)
        file_path = get_source_path(self.repo, log=self.log)
        if file_path.suffix == '.sources':
            repo = Source_obj(filename=file_path.name)
        elif file_path.suffix == '.list':
            repo = LegacyDebSource(filename=file_path.name)
        
        repo.load_from_file()

        try:
            set_source_enabled(repo, self.enable)
            if self.verbose:
                print(repo.make_source_string())
            if not self.debug:
                repo.save_to_disk()
        except command.RepolibCommandError as e:
            self.log.error(
                'Could not change source code for %s:\n%s',
                self.repo,
                e
            )

        return True

def set_source_enabled(repo, enabled):
    """ Enables or disables Source Code for the given repository.

    Arguments:
        repo - Repolib.Source: The repository to enable or disable source for.
        enabled - bool: The state to which source code should be set.
    """
    try:
        if enabled:
            repo.types = [command.AptSourceType.BINARY, command.AptSourceType.SOURCE]
        else:
            repo.types = [command.AptSourceType.BINARY]
    # pylint: disable=invalid-name
    # This is a pretty widely used convention
    except Exception as e:
        raise command.RepolibCommandError(
            f'Could not set the source code for {repo.name} to {enabled}'
        ) from e
