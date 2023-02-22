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
import shutil

import dbus
import gnupg
from pathlib import Path
from urllib import request

from . import util

SKS_KEYSERVER = 'https://keyserver.ubuntu.com/'
SKS_KEYLOOKUP_PATH = 'pks/lookup?op=get&options=mr&exact=on&search=0x'

class KeyFileError(util.RepoError):
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
        self.log = logging.getLogger(__name__)
        self.tmp_path = Path()
        self.path = Path()
        self.gpg = gnupg.GPG()
        self.data = b''
        
        if name:
            self.reset_path(name=name)
            self.setup_gpg()
    
    def reset_path(self, name: str = '', path:str = '', suffix: str = 'archive-keyring') -> None:
        """Set the path for this key
        
        Arguments:
            suffix(str): The suffix to append to the end of the name to get the
                file name (default: 'archive-keyring')
            name(str): The name of the source
            path(str): The entire path to the key
        """
        self.log.info('Setting path')
        if not name and not path:
            raise KeyFileError('A name is required to set the path for this key')
        
        if name:
            file_name = f'{name}-{suffix}.gpg'
            self.tmp_path = util.TEMP_DIR / file_name
            self.path = util.KEYS_DIR / file_name
        elif path:
            self.path = Path(path)
            self.tmp_path = util.TEMP_DIR / self.path.name
        
        self.setup_gpg()
        
        self.log.debug('Key Path: %s', self.path)
        self.log.debug('Temp Path: %s', self.tmp_path)
    
    def setup_gpg(self) -> None:
        """Set up the GPG object for this key."""
        self.log.info('Setting up GPG')
        self.log.debug('Copying %s to %s', self.path, self.tmp_path)
        try:
            shutil.copy2(self.path, self.tmp_path)
        
        except FileNotFoundError:
            pass
        
        self.gpg = gnupg.GPG(keyring=str(self.tmp_path))
        self.log.debug('GPG Setup: %s', self.gpg.keyring)
    
    def save_gpg(self) -> None:
        """Saves the key to disk."""
        self.log.info('Saving key file %s from %s', self.path, self.tmp_path)
        self.log.debug('Key contents: %s', self.gpg.list_keys())
        self.log.debug('Temp key exists? %s', self.tmp_path.exists())
        if not util.KEYS_DIR.exists():
            try:
                util.KEYS_DIR.mkdir(parents=True)
            except PermissionError:
                self.log.error(
                    'Key destination path does not exist and cannot be created '
                    'Failures expected now.'
                )
        try:
            shutil.copy(self.tmp_path, self.path)
        
        except PermissionError:
            bus = dbus.SystemBus()
            privileged_object = bus.get_object('org.pop_os.repolib', '/Repo')
            privileged_object.install_signing_key(
                str(self.tmp_path),
                str(self.path)
            )
    
    def delete_key(self) -> None:
        """Deletes the key file from disk."""
        try:
            self.tmp_path.unlink()
            self.path.unlink()
        
        except PermissionError:
            bus = dbus.SystemBus()
            privileged_object = bus.get_object('org.pop_os.repolib', '/Repo')
            privileged_object.delete_signing_key(str(self.path))
        
        except FileNotFoundError:
            pass

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
        
        NOTE: The keyserver and keypath args only affect the operation of the 
            `fingerprint` keyword.
        """
        
        if self.path.exists():
            with open(self.path, mode='rb') as keyfile:
                self.data = keyfile.read()
            return
        
        self.tmp_path.touch()
        
        if 'raw' in kwargs:
            self.data = kwargs['raw']
            self.gpg.import_keys(self.data)
            return
        
        if 'ascii' in kwargs:
            self.gpg.import_keys(kwargs['ascii'])
            if self.tmp_path.exists():
                with open(self.tmp_path, mode='rb') as keyfile:
                    self.data = keyfile.read()
            return
        
        if 'url' in kwargs:
            req = request.Request(kwargs['url'])
            with request.urlopen(req) as response:
                self.data = response.read().decode('UTF-8')
                self.gpg.import_keys(self.data)
            return
        
        if 'fingerprint' in kwargs:
            if not 'keyserver' in kwargs:
                kwargs['keyserver'] = SKS_KEYSERVER
            
            if not 'keypath' in kwargs:
                kwargs['keypath'] = SKS_KEYLOOKUP_PATH
            
            key_url = kwargs['keyserver'] + kwargs['keypath'] + kwargs['fingerprint']
            req = request.Request(key_url)
            with request.urlopen(req) as response:
                self.data = response.read().decode('UTF-8')
                self.gpg.import_keys(self.data)
            return
        
        raise TypeError(
            f'load_key_data() got an unexpected keyword argument "{kwargs.keys()}',
            ' Expected keyword arguments are: [raw, ascii, url, fingerprint]'
        )
        


