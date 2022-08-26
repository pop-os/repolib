#!/usr/bin/python3

"""
Copyright (c) 2019-2022, Ian Santopietro
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
import logging.handlers as handlers

from pathlib import Path

from . import __version__

VERSION = __version__.__version__

from .file import SourceFile, SourceFileError
from .source import Source, SourceError
from .ppa import PPASource
from .popdev import PopdevSource
from .key import SourceKey, KeyFileError
from . import util

LOG_FILE_PATH = '/var/log/repolib.log'
LOG_LEVEL = logging.DEBUG
SOURCES_DIR = util.SOURCES_DIR
KEYS_DIR = util.KEYS_DIR
TESTING = util.TESTING
KEYSERVER_QUERY_URL = util.KEYSERVER_QUERY_URL
DISTRO_CODENAME = util.DISTRO_CODENAME
PRETTY_PRINT = util.PRETTY_PRINT
CLEAN_CHARS = util.CLEAN_CHARS

try:
    from systemd.journal import JournalHandler
    systemd_support = True
except ImportError:
    systemd_support = False

## Setup logging
stream_fmt = logging.Formatter(
     '%(name)-21s: %(levelname)-8s %(message)s'
)
file_fmt = logging.Formatter(
    '%(asctime)s - %(name)-21s: %(levelname)-8s %(message)s'
)
log = logging.getLogger(__name__)

console_log = logging.StreamHandler()
console_log.setFormatter(stream_fmt)
console_log.setLevel(LOG_LEVEL)

# file_log = handlers.RotatingFileHandler(
#     LOG_FILE_PATH, maxBytes=(1048576*5), backupCount=5
# )
# file_log.setFormatter(file_fmt)
# file_log.setLevel(LOG_LEVEL)

log.addHandler(console_log)
# log.addHandler(file_log)

if systemd_support:
    journald_log = JournalHandler()
    journald_log.setLevel(LOG_LEVEL)
    journald_log.setFormatter(stream_fmt)
    log.addHandler(journald_log)

log.setLevel(logging.DEBUG)

RepoError = util.RepoError
SourceFormat = util.SourceFormat
SourceType = util.SourceType
AptSourceEnabled = util.AptSourceEnabled

url_validator = util.url_validator
fetch_key = util.fetch_key
prettyprint_enable = util.prettyprint_enable
get_source_path = util.get_source_path
get_keys_dir = util.get_keys_dir
get_sources_dir = util.get_sources_dir
validate_debline = util.validate_debline
strip_hashes = util.strip_hashes
compare_sources = util.compare_sources
combine_sources = util.combine_sources
sources:dict = {}
files = util.files
keys = util.keys
errors = util.errors

valid_keys = util.valid_keys
options_inmap = util.options_inmap
options_outmap = util.options_outmap
true_values = util.true_values

def load_all_sources() -> None:
    """Loads all of the sources present on the system."""
    log.info('Loading all sources')
    sources_path = Path(SOURCES_DIR)
    sources_files = sources_path.glob('*.sources')
    legacy_files = sources_path.glob('*.list')

    for file in sources_files:
        try:
            sourcefile = SourceFile(name=file.stem)
            log.debug('Loading %s', file)
            sourcefile.load()
            if file.name not in files:
                files[file.name] = sourcefile

        except Exception as err:
            util.errors[file.name] = err
    
    for file in legacy_files:
        try:
            sourcefile = SourceFile(name=file.stem)
            sourcefile.load()
            util.files[file.name] = sourcefile
        except Exception as err:
            util.errors[file.name] = err
    
    for f in files:
        file = files[f]
        for source in file.sources:
            if source.ident in sources:
                source.ident = f'{file.name}-{source.ident}'
                source.file.save()
            sources[source.ident] = source
