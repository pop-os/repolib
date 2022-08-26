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
from sys import prefix

from repolib.key import SourceKey

from .source import Source, SourceError
from .file import SourceFile
from . import util

BASE_URL = 'http://apt.pop-os.org/staging/'
BASE_FORMAT = util.SourceFormat.DEFAULT
BASE_COMPS = 'main'
BASE_KEYURL = 'https://raw.githubusercontent.com/pop-os/pop/master/scripts/.iso.asc'

prefix = 'popdev'
delineator = ':'

class PopdevSource(Source):
    """ PopDev Source shortcut

    These are given in the format popdev:branchname. 

    Arguments:
        shortcut (str): The ppa: shortcut to process
    """

    @staticmethod
    def validator(shortcut:str) -> None:
        """Determine whether a PPA shortcut is valid.
        
        Arguments:
            shortcut(str): The shortcut to validate
        
        Returns: bool
            `True` if the PPA is valid, otherwise False
        """

        if shortcut.startswith(prefix):
            shortlist = shortcut.split('/')
            if len(shortlist) > 0:
                return True
        return False

    def __init__(self, *args, line=None, fetch_data=True, **kwargs):
        if line:
            if not line.startswith('ppa:'):
                raise SourceError(f'The PPA shortcut {line} is malformed')
        super().__init__(args, kwargs)
        self.log = logging.getLogger(__name__)
        self.line = line
        self.twin_source = True
        if line:
            self.load_from_shortcut(self.line)

    def load_from_shortcut(self, shortcut:str='', meta:bool=True, key:bool=True) -> None:
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
        
        self.info_parts = shortcut.split(delineator)
        branch_name = self.info_parts[1:]

        self.ident = f'{prefix}-{branch_name}'
        if f'{self.ident}.{BASE_FORMAT.value}' not in util.files:
            new_file = SourceFile(name=self.ident)
            new_file.format = BASE_FORMAT
            self.file = new_file
            util.files[str(self.file.path)] = self.file
        else:
            self.file = util.files[str(self.file.path)]
        
        self.file.add_source(self)
        
        self.name = f'Pop Development Branch {branch_name}'
        self.uris = [f'{BASE_URL}/{branch_name}']
        self.suites = [util.DISTRO_CODENAME]
        self.components = [BASE_COMPS]

        key = SourceKey(name='popdev')
        key.load_key_data(url=BASE_KEYURL)
        self.key = key
        self.signed_by = str(self.key.path)

        self.enabled = True
