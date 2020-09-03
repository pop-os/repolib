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

    # pylint: disable=super-init-not-called
    # Because this is a sort of meta-source, it needs to be different from the
    # super class.
    def __init__(self, *args, filename='example.list', **kwargs):
        super().__init__(*args, filename=filename, **kwargs)
        self.sources = []
        self['Enabled'] = ''
        self._uris = []
        self._suites = []
        self._components = []
        self._source_code_enabled = False
        self.init_values()

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

    # pylint: disable=arguments-differ
    # This is operating on a very different kind of source, thus needs to be
    # different.
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
    def name(self):
        """str: The name for this source."""
        try:
            return self['X-Repolib-Name']
        except AttributeError:
            try:
                return self.sources[0].name
            except IndexError:
                return self.filename.replace('.list', '')

    @name.setter
    def name(self, name):
        self['X-Repolib-Name'] = name

    # pylint: disable=no-else-return
    # We're returning outside the else. It shouldn't be failing.

    @property
    def enabled(self):
        """ util.AptSourceEnabled: Whether the source is enabled or not. """
        if self['Enabled']:
            return util.AptSourceEnabled(self['Enabled'])
        else:
            self['Enabled'] = self.sources[0].enabled.value
        return util.AptSourceEnabled(self['Enabled'])

    @enabled.setter
    def enabled(self, enable):
        """ Accept a wide variety of data types/values for ease of use.

        We also only operate on Binary package repositories, as source code
        repos are handled through the `types` property.
        """
        if enable in [True, 'Yes', 'yes', 'YES', 'y', 'Y', 1]:
            self['Enabled'] = 'yes'
            for repo in self.sources:
                if util.AptSourceType.BINARY in repo.types:
                    repo.enabled = True
                if util.AptSourceType.SOURCE in repo.types:
                    repo.enabled = self._source_code_enabled
        else:
            self['Enabled'] = 'no'
            for repo in self.sources:
                repo.enabled = False

    @property
    def source_code_enabled(self):
        """bool: whether source code should be enabled or not."""
        code = False
        for repo in self.sources:
            if repo.enabled == util.AptSourceEnabled.TRUE:
                if util.AptSourceType.SOURCE in repo.types:
                    code = True

        self._source_code_enabled = code
        return self._source_code_enabled

    @source_code_enabled.setter
    def source_code_enabled(self, enabled):
        """This needs to be tracked somewhat separately"""
        self._source_code_enabled = enabled
        for repo in self.sources:
            if util.AptSourceType.SOURCE in repo.types:
                repo.enabled = self.enabled

    @property
    def types(self):
        """ list of util.AptSourceTypes: The types of packages provided.

        We want to list anything that's enabled in the file.
        """
        binary = False
        code = False
        for repo in self.sources:
            if repo.enabled:
                if util.AptSourceType.BINARY in repo.types:
                    binary = True
                if util.AptSourceType.SOURCE in repo.types:
                    code = True

        types = []
        if binary:
            types.append(util.AptSourceType.BINARY)
        if code:
            types.append(util.AptSourceType.SOURCE)

        self['types'] = 'deb'
        if len(types) > 1:
            self['types'] = 'deb deb-src'
            self._source_code_enabled = True
        
        return types

    @types.setter
    def types(self, types):
        """
        This source type doesn't directly store the list of types, so instead
        we need to look at the input and determine how to apply changes to the
        various sources inside this one.
        """
        otypes = 'deb'
        if types == [util.AptSourceType.BINARY]:
            self._source_code_enabled = False
        else:
            otypes += ' deb-src'
            self._source_code_enabled = True
        
        self['Types'] = otypes

        if self.enabled:
            for repo in self.sources:
                if util.AptSourceType.SOURCE in repo.types:
                    repo.enabled = self._source_code_enabled

    @property
    def uris(self):
        """ [str]: The list of URIs providing packages. """
        if self._uris:
            self['URIs'] = self._uris
            return self._uris
        else:
            for repo in self.sources:
                if repo.uris[0] not in self._uris:
                    self._uris.append(repo.uris[0])
        self['URIs'] = self._uris
        return self._uris

    @uris.setter
    def uris(self, uris):
        """ If the user tries to remove the last URI, disable instead. """
        if len(uris) > 0:
            for repo in self.sources:
                repo.uris = self._uris
            self._uris = self['URIs'] = uris
        else:
            self.enabled = False

    @property
    def suites(self):
        """ [str]: The list of enabled Suites. """
        if self._suites:
            self['Suites'] = self._suites
            return self._suites
        else:
            for repo in self.sources:
                if repo.suites[0] not in self._suites:
                    self._suites.append(repo.suites[0])
        self['Suites'] = self._suites
        return self._suites

    @suites.setter
    def suites(self, suites):
        """ If user removes the last suite, disable instead. """
        if len(suites) > 0:
            for repo in self.sources:
                repo.suites = self._suites
            self._suites = self['Suites'] = suites 
        else:
            self.enabled = False

    @property
    def components(self):
        """[str]: The list of components enabled. """
        for repo in self.sources:
            for component in repo.components:
                if component not in self._components:
                    self._components.append(component)
        self['Components'] = self._components
        return self._components

    @components.setter
    def components(self, components):
        if len(components) > 0:
            for repo in self.sources:
                repo.components = components.copy()
        else:
            self.enabled = False

    @property
    def options(self):
        """ dict: Addtional options for the repository."""
        opts = {}
        for repo in self.sources:
            try:
                opts.update(repo.options)
            except TypeError:
                pass

        if opts:
            return opts
        return {}

    @options.setter
    def options(self, options):
        if options:
            for repo in self.sources:
                repo.options = options.copy()
        else:
            for repo in self.sources:
                repo.options = None
