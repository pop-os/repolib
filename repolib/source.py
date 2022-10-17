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

import logging
from pathlib import Path

from debian import deb822

from .parsedeb import ParseDeb
from .key import SourceKey
from . import util

DEFAULT_FORMAT = util.SourceFormat.LEGACY

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
        file(SourceFile): The file this source belongs to
        key(SourceKey): The key which signs this source
    """

    default_format = DEFAULT_FORMAT

    @staticmethod
    def validator(shortcut:str) -> bool:
        """Determine whether a deb line is valid.
        
        Arguments:
            shortcut(str): The shortcut to validate
        
        Returns: bool
            `True` if the PPA is valid, otherwise False
        """
        shortcut_list:list = shortcut.split()

        if not shortcut.startswith('deb'):
            return False
        
        if not len(shortcut_list) > 3:
            return False

        if not util.validate_debline:
            return False
        
        if len(shortcut_list) == 3 and '/' not in shortcut_list[-1]:
            return False
            
        return True

    def __init__(self, *args, file=None, **kwargs) -> None:
        """Initialize this source object"""
        self.log = logging.getLogger(__name__)
        super().__init__(*args, **kwargs)
        self.reset_values()
        self.file = file
        self.twin_source = False
        self.twin_enabled = False
    
    def __repr__(self):
        """type: () -> str"""
        # Append comments to the item
        # if self.options:

        if self.comments:
            self['Comments'] = '# '
            self['Comments'] += ' # '.join(self.comments)

        rep:str = '{%s}' % ', '.join(['%r: %r' % (k, v) for k, v in self.items()])

        rep:str = '{'
        for key in self:
            rep += f"{util.PRETTY_PRINT}'{key}': '{self[key]}', "

        rep = rep[:-2]
        rep += f"{util.PRETTY_PRINT.replace(' ', '')}"
        rep += '}'

        if self.comments:
            self.pop('Comments')

        return rep
    
    def __bool__(self) -> bool:
        has_uri:bool = len(self.uris) > 0
        has_suite:bool = len(self.suites) > 0
        has_component:bool = len(self.components) > 0

        if has_uri and has_suite and has_component:
            return True
        return False


    def get_description(self) -> str:
        """Get a UI-compatible description for a source. 
        
        Returns: (str)
            The formatted description.
        """
        return self.name
    
    def reset_values(self) -> None:
        """Reset the default values for all attributes"""
        self.log.info('Resetting source info')
        self.ident = ''
        self.name = ''
        self.enabled = True
        self.types = [util.SourceType.BINARY]
        self.uris = []
        self.suites = []
        self.components = []
        self.comments = []
        self.signed_by = None
        self.architectures = ''
        self.languages = ''
        self.targets = ''
        self.pdiffs = ''
        self.by_hash = ''
        self.allow_insecure = ''
        self.allow_weak = ''
        self.allow_downgrade_to_insecure = ''
        self.trusted = ''
        self.signed_by = ''
        self.check_valid_until = ''
        self.valid_until_min = ''
        self.valid_until_max = ''
        self.prefs = ''
        self._update_legacy_options()
        self.file = None
        self.key = None

    def load_from_data(self, data:list) -> None:
        """Loads source information from the provided data

        Should correctly load either a lecagy Deb line (optionally with 
        preceeding comment) or a DEB822 source.
        
        Arguments:
            data(list): the data to load into the source.
        """
        self.log.info('Loading source from data')
        self.reset_values()
        
        if util.validate_debline(data[0]): # Legacy Source
            if len(data) > 1:
                raise SourceError(
                    f'The source is a legacy source but contains {len(data)} entries. '
                    'It may only contain one entry.'
                )
            deb_parser = ParseDeb()
            parsed_debline = deb_parser.parse_line(data[0])
            self.ident = parsed_debline['ident']
            self.name = parsed_debline['name']
            self.enabled = parsed_debline['enabled']
            self.types = [parsed_debline['repo_type']]
            self.uris = [parsed_debline['uri']]
            self.suites = [parsed_debline['suite']]
            self.components = parsed_debline['components']
            for key in parsed_debline['options']:
                self[key] = parsed_debline['options'][key]
            self._update_legacy_options()
            for comment in parsed_debline['comments']:
                self.comments.append(comment)
            if self.comments == ['']:
                self.comments = []
            
            if not self.name:
                self.name = self.generate_default_name()

            if self.signed_by:
                self.load_key()
            return

        # DEB822 Source
        super().__init__(sequence=data)
        if self.signed_by:
            self.load_key()
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
        types = [util.SourceType.BINARY]
        if enabled in util.true_values:
            types.append(util.SourceType.SOURCECODE)
        self.types = types


    def generate_default_ident(self, prefix='') -> str:
        """Generates a suitable ID for the source
        
        Returns: str
            A sane default-id
        """
        ident:str = ''
        if len(self.uris) > 0:
            uri:str = self.uris[0].replace('/', ' ')
            uri_list:list = uri.split()
            uri_str:str = '-'.join(uri_list[1:])
            branch_name:str = util.scrub_filename(uri_str)
            ident = f'{prefix}{branch_name}'
        ident += f'-{self.types[0].ident()}'
        try:
            if not self['X-Repolib-ID']:
                self['X-Repolib-ID'] = ident
        except KeyError:
            self['X-Repolib-ID'] = ident
        return ident
    
    def generate_default_name(self) -> str:
        """Generate a default name based on the ident
        
        Returns: str
            A name based on the ident
        """
        name:str = self.ident
        try:
            name = self['X-Repolib-Name']
        except KeyError:
            self['X-Repolib-Name'] = self.ident
            return self['X-Repolib-Name']

        if not name:
            self['X-Repolib-Name'] = self.ident
        
        return self['X-Repolib-Name']

    def load_key(self, ignore_errors:bool = True) -> None:
        """Finds and loads the signing key from the system
        
        Arguments:
            ignore_errors(bool): If `False`, throw a SourceError exception if
                the key can't be found/doesn't exist (Default: `True`)
        """
        self.log.info('Finding key for source %s', self.ident)
        if not self.signed_by:
            if ignore_errors:
                self.log.warning('No key configured for source %s', self.ident)
            else:
                raise SourceError('No key configured for source {self.ident}')
        
        if self.signed_by not in util.keys:
            new_key = SourceKey()
            new_key.reset_path(path=self.signed_by)
            self.key = new_key
            util.keys[str(new_key.path)] = new_key
        else:
            self.key = util.keys[self.signed_by]

    def save(self) -> None:
        """Proxy method to save the source"""
        if not self.file == None:
            self.file.save()

    def output_legacy(self) -> str:
        """Outputs a legacy representation of this source
        
        Note: this is expected to fail if there is more than one type, URI, or
        Suite; the one-line format does not support having multiple of these
        properties.

        Returns: str
            The source output formatted as Legacy
        """
        return self.legacy

    def output_822(self) -> str:
        """Outputs a DEB822 representation of this source
        
        Returns: str
            The source output formatted as Deb822
        """
        return self.deb822
    
    def output_ui(self) -> str:
        """Outputs a string representation of this source for use in UIs
        
        Returns: str
            The source output string
        """
        return self.ui
    
    def prop_append(self, prop:list, item:str) -> None:
        """Appends an item to a list property of this source.
        NOTE: List properties are `types`, `uris`, `suites`, and `components`.

        Arguments:
            prop(list): The property on which to append the item.
            item(str): The item to append to the propery
        """
        _list = prop
        _list.append(item)
        prop = _list

    def tasks_save(self, *args, **kwargs) -> None:
        """Extra tasks to perform when saving a source"""
        return

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
        ident = util.scrub_filename(ident)
        self['X-Repolib-ID'] = ident


    @property
    def name(self) -> str: 
        """The human-friendly name for this source"""
        try:
            _name = self['X-Repolib-Name']
        except KeyError:
            _name = ''

        if not _name:
            self.generate_default_name()
        return self['X-Repolib-Name']
    
    @name.setter
    def name(self, name: str) -> None:
        self['X-Repolib-Name'] = name
    

    @property
    def enabled(self) -> util.AptSourceEnabled:
        """Whether or not the source is enabled/active"""
        try:
            enabled = self['Enabled'] in util.true_values
        except KeyError:
            return util.AptSourceEnabled.FALSE
        
        if enabled and self.has_required_parts:
            return util.AptSourceEnabled.TRUE
        return util.AptSourceEnabled.FALSE
    
    @enabled.setter
    def enabled(self, enabled) -> None:
        """For convenience, accept a wide varietry of input value types"""
        self['Enabled'] = 'no'
        if enabled in util.true_values:
            self['Enabled'] = 'yes'
    

    @property
    def types(self) -> list:
        """The list of source types for this source"""
        _types:list = []
        try:
            for sourcetype in self['types'].split():
                _types.append(util.SourceType(sourcetype))
        except KeyError:
            pass
        return _types
    
    @types.setter
    def types(self, types: list) -> None:
        """Turn this list into a string of values for storage"""
        self['Types'] = ''
        _types:list = []
        for sourcetype in types:
            if sourcetype not in _types:
                _types.append(sourcetype)
        for sourcetype in _types:
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
            return self['Suites'].split()
        except KeyError:
            return []
    
    @suites.setter
    def suites(self, suites: list) -> None:
        self['Suites'] = ' '.join(suites).strip()


    @property
    def components(self) -> list:
        """The list of URIs for this source"""
        try:
            return self['Components'].split()
        except KeyError:
            return []
    
    @components.setter
    def components(self, components: list) -> None:
        self['Components'] = ' '.join(components).strip()


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
    
    @property
    def prefs(self):
        """The path to any apt preferences files for this source."""
        try:
            prefs = self['X-Repolib-Prefs']
        except KeyError: 
            prefs = ''
        
        if prefs:
            return Path(prefs)
        return Path()
    
    @prefs.setter
    def prefs(self, prefs):
        """Accept a str or a Path-like object"""
        try:
            del self['X-Repolib-Prefs']
        except KeyError:
            pass
        
        if prefs:
            prefs_str = str(prefs)
            self['X-Repolib-Prefs'] = prefs_str
    

    ## Option properties

    @property
    def architectures (self) -> str:
        """architectures option"""
        try:
            return self['Architectures']
        except KeyError:
            return ''
    
    @architectures.setter
    def architectures(self, data) -> None:
        try:
            self.pop('Architectures')
        except KeyError:
            pass

        if data:
            self['Architectures'] = data
        self._update_legacy_options()


    @property
    def languages (self) -> str:
        """languages option"""
        try:
            return self['Languages']
        except KeyError:
            return ''
    
    @languages.setter
    def languages(self, data) -> None:
        try:
            self.pop('Languages')
        except KeyError:
            pass

        if data:
            self['Languages'] = data
        self._update_legacy_options()


    @property
    def targets (self) -> str:
        """targets option"""
        try:
            return self['Targets']
        except KeyError:
            return ''
    
    @targets.setter
    def targets(self, data) -> None:
        try:
            self.pop('Targets')
        except KeyError:
            pass

        if data:
            self['Targets'] = data
        self._update_legacy_options()


    @property
    def pdiffs (self) -> str:
        """pdiffs option"""
        try:
            return self['Pdiffs']
        except KeyError:
            return ''
    
    @pdiffs.setter
    def pdiffs(self, data) -> None:
        try:
            self.pop('Pdiffs')
        except KeyError:
            pass

        if data:
            self['Pdiffs'] = data
        self._update_legacy_options()


    @property
    def by_hash (self) -> str:
        """by_hash option"""
        try:
            return self['By-Hash']
        except KeyError:
            return ''
    
    @by_hash.setter
    def by_hash(self, data) -> None:
        try:
            self.pop('By-Hash')
        except KeyError:
            pass

        if data:
            self['By-Hash'] = data
        self._update_legacy_options()


    @property
    def allow_insecure (self) -> str:
        """allow_insecure option"""
        try:
            return self['Allow-Insecure']
        except KeyError:
            return ''
    
    @allow_insecure.setter
    def allow_insecure(self, data) -> None:
        try:
            self.pop('Allow-Insecure')
        except KeyError:
            pass

        if data:
            self['Allow-Insecure'] = data
        self._update_legacy_options()


    @property
    def allow_weak (self) -> str:
        """allow_weak option"""
        try:
            return self['Allow-Weak']
        except KeyError:
            return ''
    
    @allow_weak.setter
    def allow_weak(self, data) -> None:
        try:
            self.pop('Allow-Weak')
        except KeyError:
            pass

        if data:
            self['Allow-Weak'] = data
        self._update_legacy_options()


    @property
    def allow_downgrade_to_insecure (self) -> str:
        """allow_downgrade_to_insecure option"""
        try:
            return self['Allow-Downgrade-To-Insecure']
        except KeyError:
            return ''
    
    @allow_downgrade_to_insecure.setter
    def allow_downgrade_to_insecure(self, data) -> None:
        try:
            self.pop('Allow-Downgrade-To-Insecure')
        except KeyError:
            pass

        if data:
            self['Allow-Downgrade-To-Insecure'] = data
        self._update_legacy_options()


    @property
    def trusted (self) -> str:
        """trusted option"""
        try:
            return self['Trusted']
        except KeyError:
            return ''
    
    @trusted.setter
    def trusted(self, data) -> None:
        try:
            self.pop('Trusted')
        except KeyError:
            pass

        if data:
            self['Trusted'] = data
        self._update_legacy_options()


    @property
    def signed_by (self) -> str:
        """signed_by option"""
        try:
            return self['Signed-By']
        except KeyError:
            return ''
    
    @signed_by.setter
    def signed_by(self, data) -> None:
        try:
            self.pop('Signed-By')
        except KeyError:
            pass

        if data:
            self['Signed-By'] = data
        self._update_legacy_options()


    @property
    def check_valid_until (self) -> str:
        """check_valid_until option"""
        try:
            return self['Check-Valid-Until']
        except KeyError:
            return ''
    
    @check_valid_until.setter
    def check_valid_until(self, data) -> None:
        try:
            self.pop('Check-Valid-Until')
        except KeyError:
            pass

        if data:
            self['Check-Valid-Until'] = data
        self._update_legacy_options()


    @property
    def valid_until_min (self) -> str:
        """valid_until_min option"""
        try:
            return self['Valid-Until-Min']
        except KeyError:
            return ''
    
    @valid_until_min.setter
    def valid_until_min(self, data) -> None:
        try:
            self.pop('Valid-Until-Min')
        except KeyError:
            pass

        if data:
            self['Valid-Until-Min'] = data
        self._update_legacy_options()


    @property
    def valid_until_max (self) -> str:
        """valid_until_max option"""
        try:
            return self['Valid-Until-Max']
        except KeyError:
            return ''
    
    @valid_until_max.setter
    def valid_until_max(self, data) -> None:
        try:
            self.pop('Valid-Until-Max')
        except KeyError:
            pass

        if data:
            self['Valid-Until-Max'] = data
        self._update_legacy_options()
    
    @property
    def default_mirror(self) -> str:
        """The default mirror/URI for the source"""
        try:
            return self['X-Repolib-Default-Mirror']
        except KeyError:
            return ''
    
    @default_mirror.setter
    def default_mirror(self, mirror) -> None:
        if mirror:
            self['X-Repolib-Default-Mirror'] = mirror
        else:
            self['X-Repolib-Default-Mirror'] = ''


    ## Output Properties
    @property
    def deb822(self) -> str:
        """The DEB822 representation of this source"""
        self._update_legacy_options()
        # comments get handled separately because they're a list, and list
        # properties don't support .append()
        if self.comments:
            self['X-Repolib-Comments'] = '# '
            self['X-Repolib-Comments'] += ' # '.join(self.comments)
        _deb822 = self.dump()
        if self.comments:
            self.pop('X-Repolib-Comments')
        if _deb822:
            return _deb822
        return ''
    
    @property
    def ui(self) -> str:
        """The UI-friendly representation of this source"""
        self._update_legacy_options()
        _ui_list:list = self.deb822.split('\n')
        ui_output: str = f'{self.ident}:\n'
        for line in _ui_list:
            key = line.split(':')[0]
            if key not in util.output_skip_keys:
                if line:
                    ui_output += f'{line}\n'
        for key in util.keys_map:
            ui_output = ui_output.replace(key, util.keys_map[key])
        return ui_output
    
    @property
    def legacy(self) -> str:
        """The legacy/one-line format representation of this source"""
        self._update_legacy_options()

        if str(self.prefs) != '.':
            raise SourceError(
                'Apt Preferences files can only be used with DEB822-format sources.'
            )
        
        sourcecode = self.sourcecode_enabled
        if len(self.types) > 1:
            self.twin_source = True
            self.types = [util.SourceType.BINARY]
            sourcecode = True

        legacy = ''

        legacy += self._generate_legacy_output()
        if self.twin_source:
            legacy += '\n'
            legacy += self._generate_legacy_output(sourcecode=True, enabled=sourcecode)

        return legacy

    def _generate_legacy_output(self, sourcecode=False, enabled=True) -> str:
        """Generate a string of the current source in legacy format"""
        legacy = ''

        if len(self.types) > 1:
            self.twin_source = True
            self.types = [util.SourceType.BINARY]
        for attr in ['types', 'uris', 'suites']:
            if len(getattr(self, attr)) > 1:
                msg = f'The source has too many {attr}.'
                msg += f'Legacy-format sources support one {attr[:-1]} only.'
                raise SourceError(msg)
        
        if not self.enabled.get_bool() and not sourcecode:
            legacy += '# '
        
        if sourcecode and not enabled:
            legacy += '# '
        
        if sourcecode:
            legacy += 'deb-src '
        else:
            legacy += self.types[0].value
            legacy += ' '
        
        options_string = self._legacy_options()
        if options_string:
            legacy += '['
            legacy += options_string
            legacy = legacy.strip()
            legacy += '] '
        
        legacy += f'{self.uris[0]} '
        legacy += f'{self.suites[0]} '

        for component in self.components:
            legacy += f'{component} '
        
        legacy += f' ## X-Repolib-Name: {self.name}'
        legacy += f' # X-Repolib-ID: {self.ident}'
        if self.comments:
            for comment in self.comments:
                legacy += f' # {comment}'

        return legacy

    def _legacy_options(self) -> str:
        """Turn the current options into a oneline-style string
        
        Returns: str
            The one-line-format options string
        """
        options_str = ''
        for key in self.options:
            if self.options[key] != '':
                options_str += f'{key}={self.options[key].replace(" ", ",")} '
        return options_str

    def _update_legacy_options(self) -> None:
        """Updates the current set of legacy options"""
        self.options = {
            'arch': self.architectures,
            'lang': self.languages,
            'target': self.targets,
            'pdiffs': self.pdiffs,
            'by-hash': self.by_hash,
            'allow-insecure': self.allow_insecure,
            'allow-weak': self.allow_weak,
            'allow-downgrade-to-insecure': self.allow_downgrade_to_insecure,
            'trusted': self.trusted,
            'signed-by': self.signed_by,
            'check-valid-until': self.check_valid_until,
            'valid-until-min': self.valid_until_min,
            'valid-until-max': self.valid_until_max,
        }