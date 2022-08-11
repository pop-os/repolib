#!/usr/bin/python3

"""
Copyright (c) 2022, Ian Santopietro
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

from debian import deb822

from .parsedeb import ParseDeb
from .key import SourceKey
from . import util

class SourceError(util.RepoError):
    """ Exception from a source object."""

    def __init__(self, *args, code=1, **kwargs):
        """Exception with a source object

        Arguments:
            code (:obj:`int`, optional, default=1): Exception error code.
    """
        super().__init__(*args, **kwargs)
        self.code = code

class Source(deb822.Deb822):
    """A DEB822 object representing a single software source.
    
    Attributes:
        ident(str): The unique id for this source
        name(str): The user-readable name for this source
        enabled(bool): Whether or not the source is enabled
        types([SourceType]): A list of repository types for this source
        uris([str]): A list of possible URIs for this source
        suites([str]): A list of enabled suites for this source
        components([str]): A list of enabled components for this source
        comments(str): Comments for this source 
        signed_by(Path): The path to this source's key file
        options(dict): A dictionary mapping for this source's options
        file(SourceFile): The file this source belongs to
        key(SourceKey): The key which signs this source
    """

    def __init__(self, *args, file=None, line:str = None, **kwargs) -> None:
        """Initialize this source object"""
        super().__init__(*args, **kwargs)
        self.reset_values()
        self.file = file
    
    def reset_values(self) -> None:
        """Reset the default values for all attributes"""
        self.ident = ''
        self.name = ''
        self.enabled = True
        self.types = [util.SourceType.BINARY]
        self.uris = []
        self.suites = []
        self.components = []
        self.comments = ''
        self.signed_by = None
        self.options = {}
        self.file = None
        self.key = None

    def load_from_data(self, data:list) -> None:
        """Loads source information from the provided data

        Should correctly load either a lecagy Deb line (optionally with 
        preceeding comment) or a DEB822 source.
        
        Arguments:
            data(list): the data to load into the source.
        """
        self.reset_values()
        
        # Process comments
        if data[0].strip().startswith('#'):
            self.comments = util.strip_hashes(data.pop(0))
        
        if util.validate_debline(data[0]): # Legacy Source
            if len(data) > 1:
                raise SourceError(
                    f'The source is a legacy source but contains {len(data)} entries. '
                    'It may only contain one entry.'
                )
            deb_parser = ParseDeb()
            parsed_debline = deb_parser.parse_line(data[0])
            self.enabled = parsed_debline['enabled']
            self.ident = parsed_debline['ident']
            self.name = parsed_debline['name']
            self.comment = parsed_debline['comment']
            self.types = [parsed_debline['repo_type']]
            self.uris = [parsed_debline['uri']]
            self.suites = [parsed_debline['suite']]
            self.components = parsed_debline['components']
            self.options = parsed_debline['options'].copy()
            if 'signed-by' in self.options:
                self.signed_by = self.options['signed-by']
            return

        # DEB822 Source
        super().__init__(sequence=data)
        return
    
    @property
    def sourcecode_enabled(self) -> bool:
        """`True` if this source also provides source code, otherwise `False`"""
        if util.SourceType.SOURCECODE in self.types:
            return True
        return False
    
    @sourcecode_enabled.setter
    def sourcecode_enabled(self, enabled) -> None:
        """Accept a variety of input values"""
        self.types = [util.SourceType.BINARY]
        if enabled in util.true_values:
            self.types.append(util.SourceType.SOURCECODE)


    def generate_default_ident() -> str:
        """Generates a suitable ID for the source
        
        Returns: str
            A sane default-id
        """


    def set_key(key:SourceKey) -> None:
        """Sets the source signing key
        
        Arguments:
            key(SourceKey): The key to set as the signing key
        """


    def load_key() -> SourceKey:
        """Finds and loads the signing key from the system
        
        Returns: SourceKey
            The SourceKey loaded from the system, or None
        """


    def add_key() -> None:
        """Adds the source signing key to the system"""


    def remove_key() -> None:
        """Removes the source signing key from the system."""


    def output_legacy() -> str:
        """Outputs a legacy representation of this source
        
        Returns: str
            The source output formatted as Legacy
        """


    def output_822() -> str:
        """Outputs a DEB822 representation of this source
        
        Returns: str
            The source output formatted as Deb822
        """


    ## Properties are stored/retrieved from the underlying Deb822 dict
    @property
    def has_required_parts(self) -> bool:
        """(RO) True if all required attributes are set, otherwise false."""
        required_parts = ['uris', 'suites', 'ident']

        for attr in required_parts:
            if len(getattr(self, attr)) < 1:
                return False
        
        return True


    @property
    def ident(self) -> str:
        """The ident for this source within the file"""
        try:
            return self['X-Repolib-ID']
        except KeyError:
            return ''

    @ident.setter
    def ident(self, ident: str) -> None:
        ident = ident.translate(util.CLEAN_CHARS)
        self['X-Repolib-ID'] = ident


    @property
    def name(self) -> str: 
        """The human-friendly name for this source"""
        try:
            if not self['X-Repolib-Name']:
                self['X-Repolib-Name'] = self.make_default_name()
            return self['X-Repolib-Name']
        except KeyError:
            return ''
    
    @name.setter
    def name(self, name: str) -> None:
        self['X-Repolib-Name'] = name
    

    @property
    def enabled(self) -> bool:
        """Whether or not the source is enabled/active"""
        try:
            enabled = self['Enabled']
        except KeyError:
            return False
        
        if enabled and self.has_required_parts:
            return True
        return False
    
    @enabled.setter
    def enabled(self, enabled) -> None:
        """For convenience, accept a wide varietry of input value types"""
        self['Enabled'] = False
        if enabled in util.true_values:
            self['Enabled'] = True
    

    @property
    def types(self) -> list:
        """The list of source types for this source"""
        _types:list = []
        try:
            for sourcetype in self['types']:
                _types.append(util.SourceType(sourcetype))
        except KeyError:
            pass
        return _types
    
    @types.setter
    def types(self, types: list) -> None:
        """Turn this list into a string of values for storage"""
        self['Types'] = ''
        for sourcetype in types:
            self['Types'] += f'{sourcetype.value} '
        self['Types'] = self['Types'].strip()
    

    @property
    def uris(self) -> list:
        """The list of URIs for this source"""
        try:
            return self['URIs'].split()
        except KeyError:
            return []
    
    @uris.setter
    def uris(self, uris: list) -> None:
        self['URIs'] = ' '.join(uris).strip()
    

    @property
    def suites(self) -> list:
        """The list of URIs for this source"""
        try:
            return self['URIs'].split()
        except KeyError:
            return []
    
    @suites.setter
    def suites(self, suites: list) -> None:
        self['Suites'] = ' '.join(suites).strip()


    @property
    def components(self) -> list:
        """The list of URIs for this source"""
        try:
            return self['URIs'].split()
        except KeyError:
            return []
    
    @components.setter
    def components(self, components: list) -> None:
        self['Components'] = ' '.join(components).strip()
    

    @property
    def signed_by(self) -> Path:
        """The signing key for this source
        
        We want to set the underlying data for this path as well if present. 
        This will ensure the data on disk stays synced with changes to the key.
        """
        if self.key:
            self['Signed-By'] = self.key.path
            return self.key.path
        else:
            return None
    
    @signed_by.setter
    def signed_by(self, keypath:str) -> None:
        """If we get a valid key path, set a key too."""
        if keypath:
            key = SourceKey(path=keypath)
            if key.path.exists():
                self.key = key
                self['Signed-By'] = str(self.key.path)
                return


    @property
    def options(self) -> dict:
        """The options for this source"""
        return self._options
    
    @options.setter
    def options(self, options:dict) -> None:
        if 'Signed-By' in options:
            self.signed_by = options['Signed-By']
            if self.signed_by:
                options.pop('Signed-By')
        self._options = options


    def _oneline_options(self) -> str:
        """Turn the current options into a oneline-style string
        
        Returns: str
            The one-line-format options string
        """
        options_str = ''
        if self.signed_by:
            options_str += f'{util.options_outmap["Signed-By"]}={self.signed_by} '
        for key in self.options:
            options_str += f'{util.options_outmap[key]}={self.options[key].replace(" ", ",")} '
        return options_str
