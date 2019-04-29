#!/usr/bin/python3

"""
Copyright (c) 2019, Ian Santopietro
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

sources_dir = '/etc/apt/sources.list.d'

class RepoError(Exception):
    pass

class AptSourceType(Enum):
    BINARY = "deb"
    SOURCE = "deb-src"

    def get_string(self):
        return self.value

class AptSourceEnabled(Enum):
    TRUE = 'yes'
    FALSE = 'no'

    def get_bool(self):
        if self.value is "yes":
            return True
        else:
            return False
    
    def get_string(self):
        return self.value

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