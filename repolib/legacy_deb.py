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
# pylint: disable=too-many-ancestors, too-many-instance-attributes
# If we want to use the subclass, we don't have a lot of options.

import dbus

from . import deb
from . import source
from . import util

def combine_lists(list1, list2):
    """ Adds list2 to list1, without adding duplicates.

    Arguments:
        list1 (list): The list to add to
        list2 (list): The list to add from

    Returns:
        A list of the two combined.
    """
    for item in list2:
        if item not in list1:
            list1.append(item)

    return list1

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

    # pylint: disable=super-init-not-called
    # Because this is a sort of meta-source, it needs to be different from the
    # super class.
    def __init__(self, *args, filename=None, ident=None, **kwargs):
        super().__init__(*args, filename=filename, ident=ident, **kwargs)
        self.sources = []
        self._source_code_enabled = False
        self.init_values()

    def make_names(self):
        """ Creates a filename for this source, if one is not provided.

        It also sets these values up.
        """

        if len(self.sources) <= 0:
            self.name = self.make_name()

        if not self.ident:
            self.ident = self.sources[0].make_name()

        if not self.name:
            self.name = self.sources[0].make_name()
            self.name = self.name.replace('.sources', '')

    def load_from_sources(self):
        """ Loads the source from its consituent source lines."""
        enabled = False
        uris = []
        suites = []
        components = []
        options = {}

        for repo in self.sources:
            if repo.types[0] not in self.types:
                self.types.append(repo.types[0])
            if repo.enabled.value == 'yes':
                if util.AptSourceType.BINARY in repo.types:
                    enabled = True
                else:
                    self.source_code_enabled = True
            uris = combine_lists(uris, repo.uris)
            suites = combine_lists(suites, repo.suites)
            components = combine_lists(components, repo.components)
            options.update(repo.options)

        self.uris = uris.copy()
        self.suites = suites.copy()
        self.components = components.copy()
        self.options = options.copy()
        self.enabled = enabled
        self.enabled = self.enabled

        if not self.name:
            self.make_names()
            for src in self.sources:
                src.name = self.name

    def load_from_file(self, filename=None, ident=None):
        """ Loads the source from a file on disk.

        Keyword arguments:
          filename -- STR, Containing the path to the file. (default: self.filename)
        """
        self._set_filename_ident(filename, ident)
        self.sources = []
        name = None

        full_path = util.get_sources_dir() / self.filename
        sources = []
        with open(full_path, 'r') as source_file:
            for line in source_file:
                if util.validate_debline(line):
                    deb_src = deb.DebLine(line)
                    deb_src.name = self.name
                    sources.append(deb_src)
                elif "X-Repolib-Name" in line:
                    name = ':'.join(line.split(':')[1:])
                    self.name = name.strip()

        self.sources = sources
        self.load_from_sources()

    # pylint: disable=arguments-differ
    # This is operating on a very different kind of source, thus needs to be
    # different.
    def save_to_disk(self):
        """ Save the source to the disk. """
        try:
            self.sources[0].save_to_disk(save=False)
        except IndexError:
            pass
        full_path = util.get_sources_dir() / self.filename

        source_output = self.make_deblines()
        try:
            with open(full_path, 'w') as source_file:
                source_file.write(source_output)
        except PermissionError:
            bus = dbus.SystemBus()
            privileged_object = bus.get_object('org.pop_os.repolib', '/Repo')
            privileged_object.output_file_to_disk(self.filename, source_output)
            privileged_object.exit()

    def make_deblines(self):
        """ Create a string representation of the enties as they would be saved.

        This is useful for testing, and is used by the save_to_disk() method.

        Returns:
            A str with the output entries.
        """
        toprint = '## Added/managed by repolib ##\n'
        toprint += f'#\n## X-Repolib-Name: {self.name}\n'

        for suite in self.suites:
            for uri in self.uris:
                out_binary = source.Source()
                out_binary.name = self.name
                out_binary.enabled = self.enabled.value
                out_binary.types = [util.AptSourceType.BINARY]
                out_binary.uris = [uri]
                out_binary.suites = [suite]
                out_binary.components = self.components
                out_binary.options = self.options
                toprint += f'{out_binary.make_debline()}\n'

                out_source = out_binary.copy()
                out_source.enabled = self.source_code_enabled
                out_source.types = [util.AptSourceType.SOURCE]
                toprint += f'{out_source.make_debline()}\n'

        return toprint


    @property
    def source_code_enabled(self):
        """bool: whether source code should be enabled or not."""
        source_code = False
        for repo in self.sources:
            if repo.enabled == util.AptSourceEnabled.TRUE:
                if util.AptSourceType.SOURCE in repo.types:
                    source_code = True
        self._source_code_enabled = source_code
        return self._source_code_enabled

    @source_code_enabled.setter
    def source_code_enabled(self, enabled):
        """This needs to be tracked somewhat separately"""
        self._source_code_enabled = enabled
        for repo in self.sources:
            if util.AptSourceType.SOURCE in repo.types and self.enabled:
                repo.enabled = enabled

    @property
    def filename(self):
        """str: The filename of the source."""
        return f'{self.ident}.list'

    @filename.setter
    def filename(self, name):
        self._ident = self._clean_name(name)

    @property
    def types(self):
        """ list of util.AptSourceTypes: The types of packages provided.

        We need to override in order to learn this from the source_code_enabled
        property.
        """
        if self.source_code_enabled:
            self['Types'] = 'deb deb-src'
        else:
            self['Types'] = 'deb'

        types = []
        try:
            for dtype in self['Types'].split():
                types.append(util.AptSourceType(dtype.strip()))
            return types

        except KeyError:
            return []

    @types.setter
    def types(self, types):
        if util.AptSourceType.SOURCE in types:
            self.source_code_enabled = True
        else:
            self.source_code_enabled = False

        output_types = []
        for dtype in types:
            output_types.append(dtype.value)
        self['Types'] = ' '.join(output_types)
