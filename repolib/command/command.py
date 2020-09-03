
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

Command line application helper class.
"""

class Command:
    # pylint: disable=no-self-use,too-few-public-methods
    # This is a base class for other things to inherit and give other programs
    # a standardized interface for interacting with commands.
    """ CLI helper class for developing command line applications."""

    def __init__(self, log, args, parser):
        self.log = log
        self.args = args
        self.parser = parser
        if self.args.debug != 0:
            self.log.info('Debug mode set, not-saving any changes.')

    def run(self):
        """ The initial base for running the command.

        This needs to have a standardized format, argument list, and return
        either True or False depending on whether the command was successful or
        not.

        Returns:
            True if the command succeeded, otherwise False.
        """

        # Since this is just the base, it should always return True (because
        # you shouldn't fail at doing nothing).
        return True
