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

from pathlib import Path
from re import compile

from . import deb
from . import source
from . import util

options_re = compile(r'[^@.+]\[([^[]+.+)\]\ ')
uri_re = compile(r'\w+:(\/?\/?)[^\s]+')

class LegacyDebSource():

    def __init__(self, name='', filename='example.list'):
        """
        Constructor for legacy deb sources.

        Keyword Arguments:
            name (str): The name of this source
            filename (str): The name of the source file on disk
        """
        self.name = name
        self.filename = filename
        self.sources = []

    def load_from_file(self, filename=None):
        """
        Loads the source from a file on disk.

        Keyword arguments:
          filename -- STR, Containing the path to the file. (default: self.filename)
        """
        if filename:
            self.filename = filename
        self.name = ''
        self.sources = []
        
        full_path = util.sources_dir / self.filename

        with open(full_path, 'r') as source_file:
            for line in source_file:
                if self._validate(line):
                    deb_src = deb.DebLine(line)
                    self.sources.append(deb_src)
    
    def save_to_disk(self):
        full_path = util.sources_dir / self.filename

        source_output = self.make_deblines()
        
        with open(full_path, 'w') as source_file:
            source_file.write(source_output)
    
    def make_deblines(self):
        toprint = '## Added/managed by repolib ##\n'
        for source in self.sources:
            toprint += f'{source._make_debline()}\n'
        
        return toprint

    def _validate(self, valid):
        """
        Ensure we have a valid debian repository line.
        """
        valid = valid.strip()
        if valid.startswith('#'):
            valid = valid.replace('#', '')
        
        valid = valid.strip()
        
        if valid.startswith('deb'):
            return True
        
        return False
