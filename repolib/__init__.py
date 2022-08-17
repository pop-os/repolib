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
from . import __version__

VERSION = __version__.__version__

from .file import SourceFile, SourceFileError
from .source import Source, SourceError
from . import util

SOURCES_DIR = util.SOURCES_DIR
KEYS_DIR = util.KEYS_DIR
TESTING = util.TESTING
KEYSERVER_QUERY_URL = util.KEYSERVER_QUERY_URL
DISTRO_CODENAME = util.DISTRO_CODENAME
PRETTY_PRINT = util.PRETTY_PRINT
CLEAN_CHARS = util.CLEAN_CHARS

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

valid_keys = util.valid_keys
options_inmap = util.options_inmap
options_outmap = util.options_outmap
true_values = util.true_values