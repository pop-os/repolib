#!/usr/bin/python3

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

This subpackage contains tools for use in developing CLI applications using
repolib. apt-manage uses this library.
"""
#pylint: disable=invalid-name,cyclic-import
# Can't seem to find the cyclic import being complained about.

from .argparser import get_argparser
from .add import Add
from .list import List
from .modify import Modify
from .remove import Remove
from .source import Source

parser = get_argparser()
