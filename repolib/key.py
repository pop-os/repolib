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

import gnupg

from pathlib import Path
from urllib import request

from . import util

KEYS_DIR = Path(util.KEYS_DIR)
SKS_KEYSERVER = 'https://keyserver.ubuntu.com/'
SKS_KEYLOOKUP_PATH = 'pks/lookup?op=get&options=mr&exact=on&search=0x'

class KeyError(util.RepoError):
    """ Exceptions related to apt key files."""

    def __init__(self, *args, code=1, **kwargs):
        """Exceptions related to apt key files.

        Arguments:
            code (:obj:`int`, optional, default=1): Exception error code.
    """
        super().__init__(*args, **kwargs)
        self.code = code

class SourceKey:
    """A signing key for an apt source."""

    def __init__(self, name:str = '') -> None:
        self.path = None
        self.gpg = None
        self.data = None
        
        if name:
            self.set_path(name=name)
            self.setup_gpg()
    
    def reset_path(self, name: str = '', path:str = '', suffix: str = 'archive-keyring') -> None:
        """Set the path for this key
        
        Arguments:
            suffix(str): The suffix to append to the end of the name to get the
                file name (default: 'archive-keyring')
            name(str): The name of the source
            path(str): The entire path to the key
        """
        if not name and not path:
            raise KeyError('A name is required to set the path for this key')
        
        if name:
            file_name = f'{name}-{suffix}.gpg'
            self.path = KEYS_DIR / file_name
        elif path:
            self.path = Path(path)
        self.setup_gpg()
    
    def setup_gpg(self) -> None:
        """Set up the GPG object for this key."""
        self.gpg = gnupg.GPG(keyring=str(self.path))

    def load_key_data(self, **kwargs) -> None:
        """Loads the key data from disk into the object for processing.

        Each of the keyword options specifies one place to look to import key 
        data. Once one is successfully imported, the method returns, so passing 
        multiple won't import multiple keys. 
        
        Keyword Arguments:
            raw(bytes): Raw data to import to the keyring
            ascii(str): ASCII-armored key data to import directly
            url(str): A URL to download key data from
            fingerprint(str): A key fingerprint to download from `keyserver`
                keyserver(str): A keyserver to download from.
                keypath(str): The path on the keyserver from which to download.
        """
        self.setup_gpg()
        
        if self.path.exists():
            with open(self.path, mode='r') as keyfile:
                self.data = keyfile.readlines()
            return
        
        if 'raw' in kwargs:
            self.gpg.import_keys(kwargs['raw'])
            self.data = kwargs['raw']
            return
        
        if 'ascii' in kwargs:
            self.gpg.import_keys(kwargs['ascii'])
            return
        
        if 'url' in kwargs:
            req = request.Request(kwargs['url'])
            with request.urlopen(req) as response:
                self.gpg.import_keys(response.read().decode('UTF-8'))
            return
        
        if 'fingerprint' in kwargs:
            if not 'keyserver' in kwargs:
                kwargs['keyserver'] = SKS_KEYSERVER
            
            if not 'keypath' in kwargs:
                kwargs['keypath'] = SKS_KEYLOOKUP_PATH
            
            key_url = kwargs['keyserver'] + kwargs['keypath'] + kwargs['fingerprint']
            req = request.Request(key_url)
            with request.urlopen(req) as response:
                self.gpg.import_keys(response.read().decode('UTF-8'))
            return
        
        raise TypeError(
            f'load_key_data() got an unexpected keyword argument "{kwargs.keys}',
            ' Expected keyword arguments are: [raw, ascii, url, fingerprint]'
        )
        


