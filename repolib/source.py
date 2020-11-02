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

import re

import dbus
from debian import deb822

from . import util


class SourceError(Exception):
    """ Exception from a source object."""

    def __init__(self, *args, code=1, **kwargs):
        """Exception with a source object

        Arguments:
            code (:obj:`int`, optional, default=1): Exception error code.
    """
        super().__init__(*args, **kwargs)
        self.code = code

class Source(deb822.Deb822):
    """ A Deb822 object representing a software source.

    Provides a dict-like interface for accessing and modifying DEB822-format
    sources, as well as options for loading and saving them from disk.
    """
    # pylint: disable=too-many-instance-attributes
    # We want to provide easy access to these data

    options_d = {
        'arch': 'Architectures',
        'lang': 'Languages',
        'target': 'Targets',
        'pdiffs': 'PDiffs',
        'by-hash': 'By-Hash',
        'allow-insecure': 'Allow-Insecure',
        'allow-weak': 'Allow-Weak',
        'allow-downgrade-to-insecure': 'Allow-Downgrade-To-Insecure',
        'trusted': 'Trusted',
        'signed-by': 'Signed-By',
        'check-valid-until': 'Check-Valid-Until',
        'valid-until-min': 'Valid-Until-Min',
        'valid-until-max': 'Valid-Until-Max'
    }

    outoptions_d = {
        'Architectures': 'arch',
        'Languages': 'lang',
        'Targets': 'target',
        'PDiffs': 'pdiffs',
        'By-Hash': 'by-hash',
        'Allow-Insecure': 'allow-insecure',
        'Allow-Weak': 'allow-weak',
        'Allow-Downgrade-To-Insecure': 'allow-downgrade-to-insecure',
        'Trusted': 'trusted',
        'Signed-By': 'signed-by',
        'Check-Valid-Until': 'check-valid-until',
        'Valid-Until-Min': 'valid-until-min',
        'Valid-Until-Max': 'valid-until-max'
    }
    options_re = re.compile(r'[^@.+]\[([^[]+.+)\]\ ')
    uri_re = re.compile(r'\w+:(\/?\/?)[^\s]+')

    def __init__(self, *args, filename=None, ident=None, **kwargs):
        super().__init__(*args, **kwargs)
        if filename:
            self.filename = filename
        if ident:
            self.ident = ident

    def load_from_file(self, filename=None, ident=None):
        """ Loads the data from a file path.

        Arguments:
            filename (str): The name of the file on disk.
        """
        self._set_filename_ident(filename, ident)
        if not self.ident:
            raise SourceError("No filename to load from")

        full_path = util.get_sources_dir() / self.filename

        with open(full_path, mode='r') as source_file:
            super().__init__(source_file)

    def save_to_disk(self, save=True):
        """ Saves the source to disk."""
        if not self.filename:
            raise SourceError('No filename to save to specified')
        full_path = util.get_sources_dir() / self.filename

        if save:
            try:
                with open(full_path, mode='w') as sources_file:
                    sources_file.write(self.dump())
            except PermissionError:
                bus = dbus.SystemBus()
                privileged_object = bus.get_object('org.pop_os.repolib', '/Repo')
                privileged_object.output_file_to_disk(self.filename, self.dump())
                privileged_object.exit()

    def make_source_string(self):
        """ Makes a printable string of the source.

        This method is intended to provide output in a user-friendly format. For
        output representative of the actual data, use dump() instead.

        Returns:
            A str which can be printed to console.
        """
        # The source can't be enabled if there are no uris or suites
        no_uris = len(self.uris) <= 0
        no_suites = len(self.suites) <= 0
        if no_uris or no_suites:
            self.enabled = False

        if not self.name:
            self.name = self.filename.replace('.sources', '')

        toprint = self.dump()
        toprint = toprint.replace('X-Repolib-Name', 'Name')
        return toprint

    def set_source_enabled(self, enabled):
        """ Convenience method to set a source with source_code enabled.

        If source code is enabled, then the Types for self will be both
        BINARY and SOURCE. Otherwise it will be just BINARY.

        Arguments:
            enabled(bool): Wether or not to enable source-code.
        """
        if enabled:
            self.types = [util.AptSourceType.BINARY, util.AptSourceType.SOURCE]
        else:
            self.types = [util.AptSourceType.BINARY]

    # pylint: disable=arguments-differ
    # We're fundamentally doing a different thing than our super class.
    def copy(self, source_code=True):
        """ Copies the source and returns an identical source object.

        Arguments:
            source_code (bool): if True, output an identical source, except with
                source code enabled.

        Returns:
            A Source() object identical to self.
        """
        new_source = Source()
        new_source = self._copy(new_source, source_code=source_code)
        return new_source

    def make_name(self, prefix=''):
        """ Create a name for this source. """
        if len(self.uris) > 0:
            uri = self.uris[0].replace('/', ' ')
            uri_list = uri.split()
            name = '{}{}'.format(
                prefix,
                '-'.join(uri_list[1:]).translate(util.CLEAN_CHARS)
            )
        else:
            # Use the ident as a fallback as it should be good enough
            name = self.ident

        return name

    def init_values(self):
        """ Initialize the class-attributes in order.

        This ensures that the values are in the correct order when output.
        """
        self.name = ''
        self.enabled = True
        self.types = [util.AptSourceType.BINARY]
        self.uris = []
        self.suites = []
        self.components = []
        self.options = {}

    def make_debline(self):
        """ Output a one-line entry for this source.

        Note that this is expected to fail if somehow there is more than one
        type, URI, or suite, because this format does not support multiples of
        these items.
        """
        line = ''

        if len(self.uris) > 1:
            raise SourceError(
                'The source has too many URIs. One-line format sources support '
                'one URI only.'
            )
        if len(self.suites) > 1:
            raise SourceError(
                'The source has too many suites. One-line format sources support '
                'one suite only.'
            )
        if len(self.uris) > 1:
            raise SourceError(
                'The source has too many types. One-line format sources support '
                'one type only.'
            )

        if self.enabled == util.AptSourceEnabled.FALSE:
            line += '# '

        line += f'{self.types[0].value} '

        if self.options:
            line += '['
            line += self._get_options()
            line = line.strip()
            line += '] '

        line += f'{self.uris[0]} '
        line += f'{self.suites[0]} '

        for component in self.components:
            line += f'{component} '

        return line.strip()

    def _set_filename_ident(self, filename, ident):
        if filename:
            self.filename = filename
        if ident:
            self.ident = ident

    # pylint: disable=no-self-use
    # Handy to have for subclasses
    def _clean_name(self, name):
        name = name.replace('.list', '')
        name = name.replace('.sources', '')
        return name

    @property
    def name(self):
        """ str: The name of the source."""
        try:
            return self['X-Repolib-Name']
        except KeyError:
            return ""

    @name.setter
    def name(self, name):
        self['X-Repolib-Name'] = name

    @property
    def ident(self):
        """str: a system-scope identifier for this source. Used for filename."""
        try:
            return self._ident
        except AttributeError:
            self._ident = None
            return self._ident

    @ident.setter
    def ident(self, ident):
        self._ident = ident

    @property
    def filename(self):
        """str: The filename of the source."""
        return f'{self.ident}.sources'

    @filename.setter
    def filename(self, name):
        self._ident = self._clean_name(name)

    @property
    def enabled(self):
        """ util.AptSourceEnabled: Whether the source is enabled or not. """
        # The source can't be enabled if there are no uris or suites
        no_uris = len(self.uris) <= 0
        no_suites = len(self.suites) <= 0
        if no_uris or no_suites:
            return util.AptSourceEnabled.FALSE

        try:
            return util.AptSourceEnabled(self['enabled'])
        except KeyError:
            return ''

    @enabled.setter
    def enabled(self, enable):
        """ Accept a wide variety of data types/values for ease of use. """
        e_values = [True,
                    'True',
                    'true',
                    'Yes',
                    'yes',
                    'YES',
                    'y',
                    'Y',
                    util.AptSourceEnabled.TRUE,
                    1]
        if enable in e_values:
            self['Enabled'] = util.AptSourceEnabled.TRUE.value
        else:
            self['Enabled'] = util.AptSourceEnabled.FALSE.value

    @property
    def source_code_enabled(self):
        """bool: whether source code should be enabled or not."""
        code = False
        if self.enabled == util.AptSourceEnabled.TRUE:
            if util.AptSourceType.SOURCE in self.types:
                code = True

        self._source_code_enabled = code
        return self._source_code_enabled

    @source_code_enabled.setter
    def source_code_enabled(self, enabled):
        self._source_code_enabled = enabled
        self.types = [util.AptSourceType.BINARY]
        if enabled:
            self.types.append(util.AptSourceType.SOURCE)

    @property
    def types(self):
        """ list of util.AptSourceTypes: The types of packages provided. """
        try:
            types = []
            for dtype in self['Types'].split():
                types.append(util.AptSourceType(dtype.strip()))
            return types
        except KeyError:
            return []

    @types.setter
    def types(self, types):
        output_types = []
        for dtype in types:
            output_types.append(dtype.value)
        self['Types'] = ' '.join(output_types)


    @property
    def uris(self):
        """ [str]: The list of URIs providing packages. """
        try:
            return self['URIs'].split()
        except KeyError:
            return []

    @uris.setter
    def uris(self, uris):
        """ If the user tries to remove the last URI, disable as well. """
        if len(uris) > 0:
            for uri in uris:
                if not util.url_validator(uri):
                    raise SourceError(f'The URI "{uri}" is malformed.')
            self['URIs'] = ' '.join(uris)
        else:
            self['URIs'] = ''
            # self.enabled = False

    @property
    def suites(self):
        """ [str]: The list of enabled Suites. """
        try:
            return self['Suites'].split()
        except KeyError:
            return []

    @suites.setter
    def suites(self, suites):
        """ If user removes the last suite, disable as well. """
        if len(suites) > 0:
            self['Suites'] = ' '.join(suites)
        else:
            self['Suites'] = ''
            # self.enabled = False

    @property
    def components(self):
        """[str]: The list of components enabled. """
        try:
            return self['Components'].split()
        except KeyError:
            return []

    @components.setter
    def components(self, components):
        """ Also disable if the user tries to remove the last component. """
        if len(components) > 0:
            self['Components'] = ' '.join(components)
        else:
            self['Components'] = ''
            # self.enabled = False

    @property
    def options(self):
        """ dict: Addtional options for the repository."""
        non_options = [
            'X-Repolib-Name', 'Enabled', 'Types', 'URIs', 'Suites', 'Components'
        ]
        options = {}
        for key in self:
            if key not in non_options:
                options[key] = self[key]
        if len(options) > 0:
            return options
        return {}

    @options.setter
    def options(self, options):
        for key in options:
            self[key] = options[key]

    def _copy(self, new_source, source_code=False):
        new_source.name = self.name
        new_source.enabled = self.enabled
        new_source.types = self.types.copy()

        if source_code:
            new_source.types = [util.AptSourceType.SOURCE]

        new_source.uris = self.uris.copy()
        new_source.suites = self.suites.copy()
        new_source.components = self.components.copy()

        try:
            new_source.options = self.options.copy()
        except AttributeError:
            pass
        return new_source

    def _get_options(self):
        opt_str = ''
        for key in self.options:
            opt_str += f'{self.outoptions_d[key]}={self.options[key].replace(" ", ",")} '
        return opt_str
