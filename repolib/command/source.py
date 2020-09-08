
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
        self.repo = ' '.join(args.repository)
        self.enable = True
        if args.disable:
            self.enable = False

        self.verbose = False
        if args.debug > 1:
            self.verbose = True

    def run(self):
        """ Run the command."""
        if self.repo == 'x-repolib-all-sources':
            pass

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
