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

import logging

from pathlib import Path

from . import util
from .file import SourceFile
from .source import Source
from .shortcuts import popdev, ppa


log = logging.getLogger(__name__)

def load_all_sources() -> None:
    """Loads all of the sources present on the system."""
    log.info('Loading all sources')

    util.sources.clear()
    util.files.clear()
    util.keys.clear()
    util.errors.clear()

    sources_path = Path(util.SOURCES_DIR)
    sources_files = sources_path.glob('*.sources')
    legacy_files = sources_path.glob('*.list')

    for file in sources_files:
        try:
            sourcefile = SourceFile(name=file.stem)
            log.debug('Loading %s', file)
            sourcefile.load()
            if file.name not in util.files:
                util.files[file.name] = sourcefile

        except Exception as err:
            util.errors[file.name] = err
    
    for file in legacy_files:
        try:
            sourcefile = SourceFile(name=file.stem)
            sourcefile.load()
            util.files[file.name] = sourcefile
        except Exception as err:
            util.errors[file.name] = err
    
    for f in util.files:
        file = util.files[f]
        for source in file.sources:
            if source.ident in util.sources:
                source.ident = f'{file.name}-{source.ident}'
                source.file.save()
            util.sources[source.ident] = source
