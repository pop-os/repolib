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

import dbus

from repolib.key import SourceKey

from ..source import Source, SourceError
from ..file import SourceFile
from .. import util

BASE_FORMAT = util.SourceFormat.DEFAULT
BASE_URL = 'http://apt.pop-os.org/staging'
BASE_COMPS = 'main'
BASE_KEYURL = 'https://raw.githubusercontent.com/pop-os/pop/master/scripts/.iso.asc'

DEFAULT_FORMAT = util.SourceFormat.DEFAULT

prefix = 'popdev'
delineator = ':'

class PopdevSource(Source):
    """ PopDev Source shortcut

    These are given in the format popdev:branchname. 

    Arguments:
        shortcut (str): The ppa: shortcut to process
    """
    prefs_dir = Path('/etc/apt/preferences.d')
    default_format = BASE_FORMAT

    @staticmethod
    def validator(shortcut:str) -> bool:
        """Determine whether a PPA shortcut is valid.
        
        Arguments:
            shortcut(str): The shortcut to validate
        
        Returns: bool
            `True` if the PPA is valid, otherwise False
        """
        if '/' in shortcut:
            return False

        shortcut_split = shortcut.split(':')
        try:
            if not shortcut_split[1]:
                return False
        except IndexError:
            return False

        if shortcut.startswith(f'{prefix}:'):
            shortlist = shortcut.split(':')
            if len(shortlist) > 0:
                return True
                
        return False

    def __init__(self, *args, line='', fetch_data=True, **kwargs):
        if line:
            if not line.startswith('ppa:'):
                raise SourceError(f'The PPA shortcut {line} is malformed')
        super().__init__(args, kwargs)
        self.log = logging.getLogger(__name__)
        self.line = line
        self.twin_source:bool = True
        self.prefs_path = None
        self.branch_name:str = ''
        self.branch_url:str = ''
        if line:
            self.load_from_shortcut(line)
    
    def tasks_save(self, *args, **kwargs) -> None:
        super().tasks_save(*args, **kwargs)
        self.log.info('Saving prefs file for %s', self.ident)
        prefs_contents = 'Package: *\n'
        prefs_contents += f'Pin: release o=pop-os-staging-{self.branch_url}\n'
        prefs_contents += 'Pin-Priority: 1002\n'

        self.log.debug('%s prefs for pin priority:\n%s', self.ident, prefs_contents)

        try:
            with open(self.prefs, mode='w') as prefs_file:
                prefs_file.write(prefs_contents)
        except PermissionError:
            bus = dbus.SystemBus()
            privileged_object = bus.get_object('org.pop_os.repolib', '/Repo')
            privileged_object.output_prefs_to_disk(str(self.prefs), prefs_contents)
        
        self.log.debug('Pin priority saved for %s', self.ident)

    
    def get_description(self) -> str:
        return f'Pop Development Staging branch'

    
    def load_from_data(self, data: list) -> None:
        self.log.debug('Loading line %s', data[0])
        self.load_from_shortcut(shortcut=data[0])

    def load_from_shortcut(self, shortcut:str='', meta:bool=True, get_key:bool=True) -> None:
        """Translates the shortcut line into a full repo.
        
        Arguments:
            shortcut(str): The shortcut to load, if one hasn't been loaded yet.
        """
        self.reset_values()
        if shortcut:
            self.line = shortcut
        
        if not self.line:
            raise SourceError('No PPA shortcut provided')
        
        if not self.validator(self.line):
            raise SourceError(f'The line {self.line} is malformed')
        
        self.log.debug('Loading shortcut %s', self.line)
        
        self.info_parts = shortcut.split(delineator)
        self.branch_url = ':'.join(self.info_parts[1:])
        self.branch_name = util.scrub_filename(name=self.branch_url)
        self.log.debug('Popdev branch name: %s', self.branch_name)

        self.ident = f'{prefix}-{self.branch_name}'
        if f'{self.ident}.{BASE_FORMAT.value}' not in util.files:
            new_file = SourceFile(name=self.ident)
            new_file.format = BASE_FORMAT
            self.file = new_file
            util.files[str(self.file.path)] = self.file
        else:
            self.file = util.files[str(self.file.path)]
        
        self.file.add_source(self)
        
        self.name = f'Pop Development Branch {self.branch_name}'
        self.uris = [f'{BASE_URL}/{self.branch_url}']
        self.suites = [util.DISTRO_CODENAME]
        self.components = [BASE_COMPS]

        key = SourceKey(name='popdev')
        key.load_key_data(url=BASE_KEYURL)
        self.key = key
        self.signed_by = str(self.key.path)

        self.prefs_path = self.prefs_dir / f'pop-os-staging-{self.branch_name}'
        self.prefs = self.prefs_path

        self.enabled = True
