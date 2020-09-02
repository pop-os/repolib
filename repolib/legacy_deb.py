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
#pylint: disable=too-many-ancestors
# If we want to use the subclass, we don't have a lot of options.

from . import deb
from . import source
from . import util

class LegacyDebSource(source.Source):
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

    def __init__(self, *args, filename='example.list', **kwargs):
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
        self.sources = []
        name = None

        full_path = util.get_sources_dir() / self.filename

        with open(full_path, 'r') as source_file:
            for line in source_file:
                if util.validate_debline(line):
                    deb_src = deb.DebLine(line)
                    self.sources.append(deb_src)
                    deb_src.name = self.name
                elif "X-Repolib-Name" in line:
                    name = ':'.join(line.split(':')[1:])
                    self.name = name.strip()
                    

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
        toprint += f'#\n## X-Repolib-Name: {self.name}\n'
        for source in self.sources:
            toprint += f'{source.make_debline()}\n'

        return toprint

    @property
    def name(self):
        """str: The name for this source."""
        try:
            return self._name
        except AttributeError:
            try:
                return self.sources[0].name
            except IndexError:
                return self.filename.replace('.list', '')

    @name.setter
    def name(self, name):
        self._name = name
