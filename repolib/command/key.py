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

from pathlib import Path

from ..key import SourceKey
from .. import system, util

from .command import Command

KEYS_PATH = Path(util.KEYS_DIR)

class Key(Command):
    """Key subcommand.
    
    Manages signing keys for repositories, allowing adding, removal, and 
    fetching of remote keys.

    Options:
        --name, -n
        --path, -p
        --url, -u
        --ascii, -a
        --fingerprint, -f
        --keyserver, -s
        --remove, -r
    """

    @classmethod
    def init_options(cls, subparsers) -> None:
        """Sets up this command's options parser"""

        sub = subparsers.add_parser(
            'key',
            help='Manage repository signing keys',
            epilog=(
                'Note that no verification of key validity is performed when '
                'managing key using apt-mange. Ensure that keys are valid to '
                'avoid errors with updates.'
            )
        )

        sub.add_argument(
            'repository',
            default=['x-repolib-none'],
            help='Which repository to manage keys for.'
        )

        sub_group = sub.add_mutually_exclusive_group(
            required=True
        )

        sub_group.add_argument(
            '-n',
            '--name',
            help='The name of an existing key file to set.'
        )

        sub_group.add_argument(
            '-p',
            '--path',
            help='Sets a path on disk to a signing key.'
        )

        sub_group.add_argument(
            '-u',
            '--url',
            help='Download a key over HTTPS'
        )

        sub_group.add_argument(
            '-a',
            '--ascii',
            help='Add an ascii-armored key'
        )

        sub_group.add_argument(
            '-f',
            '--fingerprint',
            help=(
                'Fetch a key via fingerprint from a keyserver. Use --keyserver '
                'to specify the URL to the keyserver.'
            )
        )

        sub_group.add_argument(
            '-r',
            '--remove',
            action='store_true',
            help=(
                'Remove a signing key from the repo. If no other sources use '
                'this key, its file will be deleted.'
            )
        )

        sub.add_argument(
            '-s',
            '--keyserver',
            help=(
                'The keyserver from which to fetch the given fingerprint. '
                '(Default: keyserver.ubuntu.com)'
            )
        )
    
    def finalize_options(self, args):
        super().finalize_options(args)
        self.repo = args.repository
        self.keyserver = args.keyserver

        self.actions:dict = {}
        self.system_source = False

        for act in [
            'name',
            'path',
            'url',
            'ascii',
            'fingerprint',
            'remove',
        ]:
            self.actions[act] = getattr(args, act)
        
        system.load_all_sources()
    
    def run(self):
        """Run the command"""
        self.log.info('Modifying signing key settings for %s', self.repo)

        if not self.repo:
            self.log.error('No repository provided')
            return False
        
        try:
            self.source = util.sources[self.repo]
            if self.repo == 'system':
                self.system_source = True
        except KeyError:
            self.log.error(
                'The repository %s was not found. Check the spelling',
                self.repo
            )
            return False
        
        self.log.debug('Actions to take:\n%s', self.actions)
        self.log.debug('Source before:\n%s', self.source)

        rets = []
        for action in self.actions:
            if self.actions[action]:
                self.log.debug('Running action: %s - (%s)', action, self.actions[action])
                ret = getattr(self, action)(self.actions[action])
                rets.append(ret)
        
        self.log.debug('Results: %s', rets)
        self.log.debug('Source after: \n%s', self.source)

        if True in rets:
            self.source.file.save()
            return True
        else:
            self.log.warning('No valid changes specified, no actions taken.')
            return False
        
    def name(self, value:str) -> bool:
        """Sets the key file to a name in the key file directory"""
        if not value:
            return False
        
        key_path = None
        
        for ext in ['.gpg', '.asc']:
            if value.endswith(ext):
                path = KEYS_PATH / value
                if path.exists():
                    key_path = path
                    break
            else:
                if 'archive-keyring' not in value:
                    value += '-archive-keyring'
                path = KEYS_PATH / f'{value}{ext}'
                if path.exists():
                    key_path = path
                    break
        
        if not key_path:
            self.log.error('The key file %s could not be found', value)
            return False
        
        return self.path(str(key_path))
            
    def path(self, value:str) -> bool:
        """Sets the key file to the given path"""
        if not value:
            return False
        
        key_path = Path(value)
        
        if not key_path.exists():
            self.log.error(
                'The path %s does not exist', value
            )
            return False
        
        self.source.signed_by = str(key_path)
        self.source.load_key()
        return True

    def url(self, value:str) -> bool:
        """Downloads a key to use from a provided URL."""
        if not value:
            return False
        
        if not value.startswith('https:'):
            response = 'n'
            self.log.warning(
                'The key is not being downloaded over an encrypted connection, '
                'and may be tampered with in-transit. Only add keys that you '
                'trust, from sources which you trust.'
            )
            response = input('Do you want to continue? (y/N): ')
            if response not in util.true_values:
                return False
        
        key = SourceKey(name=self.source.ident)
        key.load_key_data(url=value)
        self.source.key = key
        self.source.signed_by = str(key.path)
        self.source.load_key()
        return True
    
    def ascii(self, value:str) -> bool:
        """Loads the key from provided ASCII-armored data"""
        if not value:
            return False
        
        response = 'n'
        print('Only add signing keys from data you trust.')
        response = input('Do you want to continue? (y/N): ')

        if response not in util.true_values:
            return False
        
        key = SourceKey(name=self.source.ident)
        key.load_key_data(ascii=value)
        self.source.key = key
        self.source.signed_by = str(key.path)
        self.source.load_key()
        return True
    
    def fingerprint(self, value:str) -> bool:
        """Downloads the key with the given fingerprint from a keyserver"""
        if not value:
            return False
        
        key = SourceKey(name=self.source.ident)
        
        if self.keyserver:
            key.load_key_data(fingerprint=value, keyserver=self.keyserver)
        else:
            key.load_key_data(fingerprint=value)
        
        self.source.key = key
        self.source.signed_by = str(key.path)
        self.source.load_key()
        return True
    
    def remove(self, value:str) -> bool:
        """Removes the key from the source"""

        if not self.source.key:
            self.log.error(
                'The source %s does not have a key configured.', 
                self.repo
            )
            return False
        
        response = 'n'
        print(
            'If you remove the key, there may no longer be any verification '
            'of software packages from this repository, including for future '
            'updates. This may cause errors with your updates.'
        )
        response = input('Do you want to continue? (y/N): ')
        if response not in util.true_values:
            return False

        old_key = self.source.key
        self.source.key = None
        self.source.signed_by = ''

        for source in util.sources.values():
            if source.key == old_key:
                self.log.info(
                    'Key file %s in use with another key, not deleting',
                    old_key.path
                )
                return True
        
        response = 'n'
        print('No other sources were found which use this key.')
        response = input('Do you want to remove it? (Y/n): ')
        if response in util.true_values:
            old_key.delete_key()
        
        return True

