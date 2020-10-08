#!/usr/bin/python3

"""
Copyright (c) 2019-2020, Ian Santopietro
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

from .source import Source
from .system import SystemSource
from .legacy_deb import LegacyDebSource
from .deb import DebLine
from .ppa import PPALine
from .util import AptSourceEnabled, AptSourceType, RepoError
from . import util
from . import ppa
from . import __version__

VERSION = __version__.__version__

def get_all_sources(get_system=False):
    """ Returns a list of all the sources on the system.

    Arguments:
        get_system (bool): Whether to include the system repository or not.
    """
    sources_path = util.get_sources_dir()
    sources_files = sources_path.glob('*.sources')
    list_files = sources_path.glob('*.list')

    sources = []

    if get_system:
        source = SystemSource()
        sources.append(source)

    for file in sources_files:
        if file.stem == 'system':
            continue
        source = Source(filename=file.stem)
        source.load_from_file()
        sources.append(source)

    for file in list_files:
        source = LegacyDebSource(filename=file.stem)
        source.load_from_file()
        sources.append(source)

    return sources
