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

from httplib2.error import ServerNotFoundError
from urllib.error import URLError

from .. import util
from ..source import Source, SourceError
from ..file import SourceFile, SourceFileError
from ..shortcuts import ppa, popdev, shortcut_prefixes
from .command import Command, RepolibCommandError

class Add(Command):
    """Add subcommand
    
    Adds a new source into the system. Requests root, if not present.
    
    Options:
        --disable, d
        --source-code, -s
        --terse, -t
        --name, -n
        --identifier, -i
        --format, -f
        --skip-keys, -k
    """

    @classmethod
    def init_options(cls, subparsers):
        """ Sets up the argument parser for this command.

        Returns: argparse.subparser
            The subparser for this command
        """

        sub = subparsers.add_parser(
            'add',
            help='Add a new repository to the system'
        )

        sub.add_argument(
            'deb_line',
            nargs='*',
            default=['822styledeb'],
            help='The deb line of the repository to add'
        )
        sub.add_argument(
            '-d',
            '--disable',
            action='store_true',
            help='Add the repository and then set it to disabled.'
        )
        sub.add_argument(
            '-s',
            '--source-code',
            action='store_true',
            help='Also enable source code packages for the repository.'
        )
        sub.add_argument(
            '-t',
            '--terse',
            action='store_true',
            help='Do not display expanded info about a repository before adding it.'
        )
        sub.add_argument(
            '-n',
            '--name',
            default='',
            help='A name to set for the new repo'
        )
        sub.add_argument(
            '-i',
            '--identifier',
            default='',
            help='The filename to use for the new source'
        )
        sub.add_argument(
            '-f',
            '--format',
            default='sources',
            help='The source format to save as, `sources` or `list`'
        )
        sub.add_argument(
            '-k',
            '--skip-keys',
            action='store_true',
            help='Skip adding signing keys (not recommended!)'
        )

        return sub

    def finalize_options(self, args):
        super().finalize_options(args)
        self.deb_line = ' '.join(args.deb_line)
        self.terse = args.terse
        self.source_code = args.source_code
        self.disable = args.disable
        self.log.debug(args)

        try:
            name = args.name.split()
        except AttributeError:
            name = args.name

        try:
            ident = args.identifier.split()
        except AttributeError:
            ident = args.identifier

        self.name = ' '.join(name)
        pre_ident:str = '-'.join(ident)
        self.ident = util.scrub_filename(pre_ident)
        self.skip_keys = args.skip_keys
        self.format = args.format.lower()
    
    def run(self) -> bool:
        """Run the command, return `True` if successful; otherwise `False`"""
        if self.deb_line == '822styledeb':
            self.parser.print_usage()
            self.log.error('A repository is required')
            return False
        
        repo_is_url = self.deb_line.startswith('http')
        repo_is_nospaced = len(self.deb_line.split()) == 1

        if repo_is_url and repo_is_nospaced:
            self.deb_line = f'deb {self.deb_line} {util.DISTRO_CODENAME} main'
        
        print('Fetching repository information...')

        self.log.debug('Adding line %s', self.deb_line)

        new_source: Source = Source()
        
        for prefix in shortcut_prefixes:
            self.log.debug('Trying prefix %s', prefix)
            if self.deb_line.startswith(prefix):
                self.log.debug('Line is prefix:  %s', prefix)
                new_source = shortcut_prefixes[prefix]()
                if not new_source.validator(self.deb_line):
                    self.log.error(
                        'The shortcut "%s" is malformed',
                        self.deb_line
                    )

                    # Try and get a suggested correction for common errors
                    try:
                        if self.deb_line[len(prefix)] != ':':
                            fixed_debline: str = self.deb_line.replace(
                                self.deb_line[len(prefix)], 
                                ":",
                                1
                            )
                            print(f'Did you mean "{fixed_debline}"?')
                    except IndexError:
                        pass
                    return False
                
                try:
                    new_source.load_from_data([self.deb_line])
                except (URLError, ServerNotFoundError) as err:
                    import traceback
                    self.log.debug(
                        'Exception info: %s \n %s \n %s',
                        type(err),
                        ''.join(traceback.format_exception(err)),
                        err.args
                    )
                    self.log.error(
                        'System is offline. A connection is required to add '
                        'PPA and Popdev sources.'
                    )
                    return False
                except Exception as err:
                    import traceback
                    self.log.debug(
                        'Exception info: %s \n %s \n %s',
                        type(err),
                        err.__traceback__,
                        err
                    )
                    self.log.error('An error ocurred: %s', err)
                    return False
                break
        
        
        if not new_source:
            self.log.error(
                f'Could not parse line "{self.deb_line}". Double-check the '
                'spelling.'
            )
            valid_shortcuts: str = ''
            for shortcut in shortcut_prefixes:
                if shortcut.startswith('deb'):
                    continue
                valid_shortcuts += f'{shortcut}, '
            valid_shortcuts = valid_shortcuts.strip(', ')
            print(f'Supported repository shortcuts:\n  {valid_shortcuts}')
            return False

        new_source.twin_source = True
        new_source.sourcecode_enabled = self.source_code

        if self.name:
            new_source.name = self.name
        if self.ident:
            new_source.ident = self.ident
        if self.disable:
            new_source.enabled = False
        
        if not new_source.ident:
            new_source.ident = new_source.generate_default_ident()

        new_file = SourceFile(name=new_source.ident)
        new_file.format = new_source.default_format
        if self.format:
            self.log.info('Setting new source format to %s', self.format)
            for format in util.SourceFormat:
                if self.format == format.value:
                    new_file.format = format
                    self.log.debug('New source format set to %s', format.value)

        new_file.add_source(new_source)
        new_source.file = new_file
        self.log.debug('File format: %s', new_file.format)
        self.log.debug('File path: %s', new_file.path)

        self.log.debug('Sources in file %s:\n%s', new_file.path, new_file.sources)
        
        if not self.terse:
            print(
                'Adding the following source: \n',
                new_source.get_description(),
                '\n\n',
                new_source.ui
            )
            try:
                input(
                    'Press ENTER to continue adding this source or Ctrl+C '
                    'to cancel'
                )
            except KeyboardInterrupt:
                # Handled here to avoid printing the exception to console
                exit(0)
        
        new_file.save()
        util.dbus_quit()
        return True
