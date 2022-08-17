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

import dbus

from .source import Source, SourceError
from . import util

SOURCES_DIR = Path(util.SOURCES_DIR)

class SourceFileError(util.RepoError):
    """ Exception from a source file."""

    def __init__(self, *args, code:int = 1, **kwargs):
        """Exception with a source file

        Arguments:
            :code int, optional, default=1: Exception error code.
    """
        super().__init__(*args, **kwargs)
        self.code: int = code

class SourceFile:
    """ A Source File on disk
    
    Attributes:
        path(Pathlib.Path): the path for this file on disk
        name(str): The name for this source (filename less the extension)
        format(SourceFormat): The format used by this source file
        contents(list): A list containing all of this file's contents
    """

    def __init__(self, name:str='') -> None:
        """Initialize a source file
        
        Arguments:
            name(str): The filename within the sources directory to load
        """
        self.name:str = ''
        self.path:Path = None
        self.format:util.SourceFormat = util.SourceFormat.DEFAULT
        self.contents:list = []
        self.sources:list = []

        if name:
            self.name = name
            self.reset_path()
            self.load()
    
    def __str__(self):
        return self.output
    
    def __repr__(self):
        return f'SourceFile(name={self.name})'
    
    def get_source_by_ident(self, ident: str) -> Source:
        """Find a source within this file by its ident
        
        Arguments:
            ident(str): The ident to search for
        
        Returns: Source
            The located source
        """
        for source in self.sources:
            if source.ident == ident:
                return source
        raise SourceFileError(
            f'The file {self.path} does not contain the source {ident}'
        )
    
    def reset_path(self) -> None:
        """Attempt to detect the correct path for this File.
        
        We default to DEB822 .sources format files, but if that file doesn't
        exist, fallback to legacy .list format. If this also doesn't exist, we
        swap back to DEB822 format, as this is likely a new file."""

        default_path = SOURCES_DIR / f'{self.name}.sources'
        legacy_path = SOURCES_DIR / f'{self.name}.list'

        if default_path.exists():
            self.path = default_path
            self.format = util.SourceFormat.DEFAULT
            return

        if legacy_path.exists():
            self.path = legacy_path
            self.format = util.SourceFormat.LEGACY
            return 
        
        self.path = default_path
        return

    def find_unique_ident(self, source1:Source, source2:Source) -> bool:
        """Takes two sources with identical idents, and finds a new, unique
        idents for them.

        The rules for this are mildly complicated, and vary depending on the
        situation:

          * (DEB822) If the sources are identical other than some portion of 
            data, then the two will be combined into a single source.
          * (legacy) If the two sources are identical other than source type 
            (common with legacy-format PPAs with source code) then the second 
            source will be dropped until export.
          * (legacy) If the sources differ by URIs, Components, or Suites, then 
            the differing data will be appended to the sources' idents.
          * (Either) If no other rules can be determined, then the sources will 
            have a number appended to them
        
        Arguments:
            source1(Source): The original source with the ident
            source2(Source): The new colliding source with the ident
        
        Returns: bool
            `True` if the two sources were successfully deduped, `False` if the
            second source should be discarded.
        """
        ident_src1:str = source1.ident
        ident_src2:str = source2.ident

        if self.format == util.SourceFormat.DEFAULT:
            util.combine_sources(source1, source2)
            ident_src2 = ''
        
        else:
            excl_keys = [
                'X-Repolib-Name',
                'X-Repolib-ID',
                'X-Repolib-Comment',
                'Enabled',
                'Types'
            ]
            if len(source1.types) == 1 and len(source2.types) == 1:
                if util.compare_sources(source1, source2, excl_keys):
                    util.combine_sources(source1, source2)
                    if source1.types == [util.SourceType.BINARY]:
                        self.sources.remove(source2)
                        self.items.remove(source2)
                        source1.sourcecode_enabled = source2.enabled
                    elif source2.types == [util.SourceType.BINARY]:
                        self.sources.remove(source1)
                        self.items.remove(source1)
                        source2.sourcecode_enabled = source1.enabled
                    ident_src2 = ''
            diffs = util.find_differences_sources(source1, source2, excl_keys)
            if diffs:
                for key in diffs:
                    raw_diffs:tuple = diffs[key]
                    diff1_list = raw_diffs[0].strip().split()
                    diff2_list = raw_diffs[1].strip().split()
                    for i in diff1_list:
                        if i not in diff2_list:
                            ident_src1 += f'-{i}'
                            break
                    for i in diff2_list:
                        if i not in diff1_list:
                            ident_src2 += f'-{i}'
                            break
                    if ident_src1 != ident_src2:
                        break
        if ident_src2 and ident_src1 != ident_src2:
            source1.ident = ident_src1
            source2.ident = ident_src2
            return True
        
        elif ident_src2 and ident_src1 == ident_src2:
            for source in self.sources:
                src_index = self.sources.index(source)
                source.ident = f'{self.name}-{src_index}'
                return True
        
        elif not ident_src2:
            return False
        
        return True

            

    def load(self) -> None:
        """Loads the sources from the file on disk"""
        self.contents = []

        if not self.name:
            raise SourceFileError('You must provide a filename to load.')
        
        if not self.path.exists():
            raise SourceFileError(f'The file {self.path} does not exist.')
        
        with open(self.path, 'r') as source_file:
            srcfile_data = source_file.readlines()
        
        item:int = 0
        raw822:list = []
        parsing_deb822:bool = False
        source_name:str = ''
        commented:bool = False
        idents:dict = {}

        # Main file parsing loop
        for line in srcfile_data:
            comment_found:str = ''
            name_line:bool = 'X-Repolib-Name' in line
            
            if not parsing_deb822:
                commented = line.startswith('#')

                # Find commented out lines
                if commented:
                    # Exclude disabled legacy deblines
                    valid_legacy = util.validate_debline(line.strip())
                    if not valid_legacy and not name_line:
                        # Found a standard comment
                        self.contents.append(line.strip())
                    
                    elif valid_legacy:
                        if self.format != util.SourceFormat.LEGACY:
                            raise SourceFileError(
                                f'File {self.ident} is an updated file, but '
                                'contains legacy-format sources. This is not '
                                'allowed. Please fix the file manually.'
                            )
                        new_source = Source()
                        new_source.load_from_data([line])
                        if source_name:
                            new_source.name = source_name
                        if not new_source.ident:
                            new_source.ident = self.name
                        if new_source.ident in idents:
                            old_source = idents[new_source.ident]
                            idents.pop(old_source.ident)
                            self.find_unique_ident(old_source, new_source)
                            idents[old_source.ident] = old_source
                        idents[new_source.ident] = new_source
                        self.contents.append(new_source)
                        self.sources.append(new_source)
                    
                    elif name_line:
                        source_name = ':'.join(line.split(':')[1:])
                        source_name = source_name.strip()
                
                # Active legacy line
                elif not commented:
                    if util.validate_debline(line.strip()):
                        if self.format != util.SourceFormat.LEGACY:
                            raise SourceFileError(
                                f'File {self.ident} is an updated file, but '
                                'contains legacy-format sources. This is not '
                                'allowed. Please fix the file manually.'
                            )
                        new_source = Source()
                        new_source.load_from_data([line])
                        if source_name:
                            new_source.name = source_name
                        if not new_source.ident:
                            new_source.ident = self.name
                        if new_source.ident in idents:
                            old_source = idents[new_source.ident]
                            idents.pop(old_source.ident)
                            self.find_unique_ident(old_source, new_source)
                            idents[old_source.ident] = old_source
                        idents[new_source.ident] = new_source
                        self.contents.append(new_source)
                        self.sources.append(new_source)
                
                # Empty lines are treated as comments
                if line.strip() == '':
                    self.contents.append('')
                
                # Find 822 sources
                # Valid sources can begin with any key:
                for key in util.valid_keys:
                    if line.startswith(key):
                        if self.format == util.SourceFormat.LEGACY:
                            raise SourceFileError(
                                f'File {self.ident} is a DEB822-format file, but '
                                'contains legacy sources. This is not allowed. '
                                'Please fix the file manually.'
                            )
                        parsing_deb822 = True
                        raw822.append(line.strip())

                item += 1
            
            elif parsing_deb822:
                # Deb822 sources are terminated with an empty line
                if line.strip() == '':
                    parsing_deb822 = False
                    new_source = Source()
                    new_source.load_from_data(raw822)
                    new_source.file = self
                    if source_name:
                        new_source.name = source_name
                    if not new_source.ident:
                            new_source.ident = self.name
                    if new_source.ident in idents:
                        old_source = idents[new_source.ident]
                        idents.pop(old_source.ident)
                        self.find_unique_ident(old_source, new_source)
                        idents[old_source.ident] = old_source
                    idents[new_source.ident] = new_source
                    self.contents.append(new_source)
                    self.sources.append(new_source)
                    raw822 = []
                    item += 1
                    self.contents.append('')
                else:
                    raw822.append(line.strip())
        
        if raw822:
            parsing_deb822 = False
            new_source = Source()
            new_source.load_from_data(raw822)
            new_source.file = self
            if source_name:
                new_source.name = source_name
            if not new_source.ident:
                new_source.ident = self.name
            if new_source.ident in idents:
                old_source = idents[new_source.ident]
                idents.pop(old_source.ident)
                self.find_unique_ident(old_source, new_source)
                idents[old_source.ident] = old_source
            idents[new_source.ident] = new_source
            self.contents.append(new_source)
            self.sources.append(new_source)
            raw822 = []
            item += 1
            self.contents.append('')

    def save(self) -> None:
        """Saves the source file to disk using the current format"""

        if not self.name or not self.format:
            raise SourceFileError('There was not a complete filename to save')
        
        if len(self.contents) > 0:
            
            try:
                with open(self.path, mode='w') as output_file:
                    output_file.write(self.output)
            
            except PermissionError:
                bus = dbus.SystemBus()
                privileged_object = bus.get_object('org.pop_os.repolib', '/Repo')
                privileged_object.output_file_to_disk(self.path.name, self.output)
        else:
            try:
                self.path.unlink()
            except PermissionError:
                bus = dbus.SystemBus()
                privileged_object = bus.get_object('org.pop_os.repolib', '/Repo')
                privileged_object.delete_source_file(self.path.name)

    
    ## Attribute properties
    @property
    def format(self) -> util.SourceFormat:
        """The format of the file on disk"""
        return self._format
    
    @format.setter
    def format(self, format:util.SourceFormat) -> None:
        """The path needs to be updated when the format changes"""
        self._format = format
        self.path = SOURCES_DIR / f'{self.name}.{self._format.value}'

    ## Output properties
    @property 
    def legacy(self) -> str:
        """Outputs the file in the output_legacy format"""
        legacy_output:str = ''
        for item in self.contents:
            try:
                legacy_output += item.legacy
            except AttributeError:
                legacy_output += item
            legacy_output += '\n'
        return legacy_output

    @property 
    def deb822(self) -> str:
        """Outputs the file in the output_822 format"""
        deb822_output:str = ''
        for item in self.contents:
            try:
                deb822_output += item.deb822
            except AttributeError:
                deb822_output += item
                deb822_output += '\n'
        return deb822_output


    @property 
    def ui(self) -> str:
        """Outputs the file in the output_ui format"""
        ui_output:str = ''
        for item in self.contents:
            try:
                ui_output += item.ui
            except AttributeError:
                pass # Skip file comments in UI mode
            ui_output += '\n'
        return ui_output


    @property 
    def output(self) -> str:
        """Outputs the file in the output format"""
        default_output:str = ''
        for item in self.contents:
            try:
                if self.format == util.SourceFormat.DEFAULT:
                    default_output += item.deb822
                elif self.format == util.SourceFormat.LEGACY:
                    default_output += item.legacy
                    default_output += '\n'
            except AttributeError:
                default_output += item
                default_output += '\n'
        return default_output
