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

from . import deb
from . import util

class LegacyDebSource():
    """Legacy deb sources

    Because Legacy Deb format entries have limitations on how many URIs or
    suites they can contain, many legacy entry files use multiple sources to
    configure multiple URIs, suites, or types. A common example is to have a
    `deb` entry and an otherwise identical `deb-src` entry. To make this
    simpler, we treat legacy sources as a "meta source" and store the individual
    lines in a list.

    Keyword Arguments:
        name (str): The name of this source
        filename (str): The name of the source file on disk
    """

    def __init__(self, name='', filename='example.list'):
        self.name = name
        self.filename = filename
        self.sources = []

    def make_names(self):
        """ Creates a filename for this source, if one is not provided.

        It also sets these values up.
        """
        self.filename = self.sources[0].make_name()
        self.filename = self.filename.replace('.sources', '.list')
        self.name = self.filename.replace('.list', '')

    def load_from_file(self, filename=None):
        """ Loads the source from a file on disk.

        Keyword arguments:
          filename -- STR, Containing the path to the file. (default: self.filename)
        """
        if filename:
            self.filename = filename
        self.name = ''
        self.sources = []

        full_path = util.get_sources_dir() / self.filename

        with open(full_path, 'r') as source_file:
            for line in source_file:
                if util.validate_debline(line):
                    deb_src = deb.DebLine(line)
                    self.sources.append(deb_src)

    def save_to_disk(self):
        """ Save the source to the disk. """
        self.sources[0].save_to_disk(save=False)
        full_path = util.get_sources_dir() / self.filename

        source_output = self.make_deblines()

        with open(full_path, 'w') as source_file:
            source_file.write(source_output)

    def make_deblines(self):
        """ Create a string representation of the enties as they would be saved.

        This is useful for testing, and is used by the save_to_disk() method.

        Returns:
            A str with the output entries.
        """
        toprint = '## Added/managed by repolib ##\n'
        toprint += f'#\n## X-Repolib-Name: {self.sources[0].name}\n'
        for source in self.sources:
            toprint += f'{source.make_debline()}\n'

        return toprint
