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

# pylint: disable=broad-except
# We want to be broad in catching exceptions here, as failure could mean
# applications unexpectedly close
def get_all_sources(get_system=False, get_exceptions=False):
    """ Returns a list of all the sources on the system.

    Arguments:
        get_system (bool): Whether to include the system repository or not.
        get_exceptions (bool): Whether to return information about failures.

    Returns:
        Without `get_exceptions`, return the :obj:`list` of :obj:`Source`
        With `get_exceptions`, return: (
            :obj:`list` of :obj:`Source`,
            :obj:`dict` of :obj:`Exception`
        )
    """
    sources_path = util.get_sources_dir()
    sources_files = sources_path.glob('*.sources')
    list_files = sources_path.glob('*.list')

    sources = []
    errors = {}

    if get_system:
        source = SystemSource()
        sources.append(source)

    for file in sources_files:
        if file.stem == 'system':
            continue
        source = Source(filename=file.name)
        try:
            source.load_from_file()
        except Exception as err:
            errors[file.stem] = err
        else:
            # The source should not be listed if it is empty
            has_uris = len(source.uris) > 0
            has_suites = len(source.suites) > 0
            if has_uris and has_suites:
                sources.append(source)

    for file in list_files:
        source = LegacyDebSource(filename=file.name)
        try:
            source.load_from_file()
        except Exception as err:
            errors[file] = err
        else:
            # The source should not be listed if it is empty
            has_uris = len(source.uris) > 0
            has_suites = len(source.suites) > 0
            if has_uris and has_suites:
                sources.append(source)

    if get_exceptions:
        return sources, errors
    return sources
