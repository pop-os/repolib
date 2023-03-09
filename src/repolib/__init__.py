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
from .shortcuts import PPASource, PopdevSource, shortcut_prefixes
from .key import SourceKey, KeyFileError
from . import util
from . import system

LOG_FILE_PATH = '/var/log/repolib.log'
LOG_LEVEL = logging.WARNING
KEYS_DIR = util.KEYS_DIR
SOURCES_DIR = util.SOURCES_DIR
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

log_level_map:dict = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG
}

if systemd_support:
    journald_log = JournalHandler() # type: ignore (this is handled by the wrapping if)
    journald_log.setLevel(logging.INFO)
    journald_log.setFormatter(stream_fmt)
    log.addHandler(journald_log)

log.setLevel(logging.DEBUG)

def set_testing(testing:bool = True) -> None:
    """Puts Repolib into testing mode"""
    global KEYS_DIR
    global SOURCES_DIR

    util.set_testing(testing=testing)
    KEYS_DIR = util.KEYS_DIR
    SOURCES_DIR = util.SOURCES_DIR


def set_logging_level(level:int) -> None:
    """Set the logging level for this current repolib

    Accepts an integer between 0 and 2, with 0 being the default loglevel of
    logging.WARNING, 1 being logging.INFO, and 2 being logging.DEBUG.

    Values greater than 2 are clamped to 2. Values less than 0 are clamped to 0.

    Note: This only affects console output. Log file output remains 
    at logging.INFO
    
    Arguments:
        level(int): A logging level from 0-2
    """
    if level > 2:
        level = 2
    if level < 0:
        level = 0
    LOG_LEVEL = log_level_map[level]
    console_log.setLevel(LOG_LEVEL)

RepoError = util.RepoError
SourceFormat = util.SourceFormat
SourceType = util.SourceType
AptSourceEnabled = util.AptSourceEnabled

scrub_filename = util.scrub_filename
url_validator = util.url_validator
prettyprint_enable = util.prettyprint_enable
validate_debline = util.validate_debline
strip_hashes = util.strip_hashes
compare_sources = util.compare_sources
combine_sources = util.combine_sources
sources = util.sources
files = util.files
keys = util.keys
errors = util.errors

valid_keys = util.valid_keys
options_inmap = util.options_inmap
options_outmap = util.options_outmap
true_values = util.true_values

load_all_sources = system.load_all_sources
