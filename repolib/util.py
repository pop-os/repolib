#!/usr/bin/python3

"""
Copyright (c) 2019-2020, Ian Santopietro
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from enum import Enum
from pathlib import Path

SOURCES_DIR = '/etc/apt/sources.list.d'
TESTING = False

class RepoError(Exception):
    """ Exception from this module."""

    def __init__(self, *args, code=1, **kwargs):
        """Exception with a source object

        Arguments:
            code (:obj:`int`, optional, default=1): Exception error code.
    """
        super().__init__(*args, **kwargs)
        self.code = code

try:
    import lsb_release
    DISTRO_CODENAME = lsb_release.get_distro_information()['CODENAME']
except ImportError:
    raise RepoError("The system can't find version information!")

class AptSourceType(Enum):
    """ Helper Enum to simplify saving data. """
    BINARY = "deb"
    SOURCE = "deb-src"

class AptSourceEnabled(Enum):
    """ Helper Enum to translate between bool data and the Deb822 format. """
    TRUE = 'yes'
    FALSE = 'no'

    def get_bool(self):
        """ Return a bool based on the value. """
        # pylint: disable=comparison-with-callable
        # This doesnt seem to actually be a callable in this case.
        if self.value == "yes":
            return True

        return False

CLEAN_CHARS = {
    33: None,
    64: 45,
    35: 45,
    36: 45,
    37: 45,
    94: 45,
    38: 45,
    42: 45,
    41: None,
    40: None,
    43: 45,
    61: 45,
    91: None,
    92: None,
    93: None,
    123: None,
    125: None,
    124: 95,
    63: None,
    47: 95,
    46: 45,
    60: 95,
    62: 95,
    44: 95,
    96: None,
    126: None,
    32: 95,
    58: None,
    59: None,
}

def get_sources_dir(testing=False):
    """ Get the path to the sources dir.

    Returns:
        pathlib.Path: The Sources dir.
    """
    # pylint: disable=global-statement
    # We want to stop using the old dir and use the testing dir on subsequent
    # calls.
    if testing:
        global SOURCES_DIR
        SOURCES_DIR = '/tmp/repolib_testing'
    # pylint: enable=global-statement
    sources_dir = Path(SOURCES_DIR)
    sources_dir.mkdir(parents=True, exist_ok=True)
    return sources_dir

def validate_debline(valid):
    """ Basic checks to see if a given debline is valid or not.

    Arguments:
        valid (str): The line to validate.

    Returns:
        True if the line is valid, False otherwise.
    """
    valid = valid.strip()
    if valid.startswith('#'):
        valid = valid.replace('#', '')

    valid = valid.strip()

    if valid.startswith('deb'):
        return True

    return False
