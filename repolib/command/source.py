
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

    def __init__(self, *args):
        super().__init__(*args)
        
        self.verbose = False
        if self.args.debug > 1:
            self.verbose = True
        
        self.repo = ' '.join(self.args.repository)