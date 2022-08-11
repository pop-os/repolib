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

from .source import Source
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

        if name:
            self.name = name
            self.set_path()
            self.load_from_disk()
    
    def set_path(self) -> None:
        """Attempt to detect the correct path for this File.
        
        We default to DEB822 .sources format files, but if that file doesn't
        exist, fallback to legacy .list format. If this also doesn't exist, we
        swap back to DEB822 format, as this is likely a new file."""

        default_path = SOURCES_DIR / f'{self.name}.sources'
        legacy_path = SOURCES_DIR / f'{self.name}.list'

        if default_path.exists():
            self.path = default_path
            return

        if legacy_path.exists():
            self.path = legacy_path
            return 
        
        self.path = default_path
        return

    def output_legacy() -> str:
        """Outputs a legacy representation of this source file
        
        Returns: str
            The Legacy-format representation of this source file
        """


    def output_822() -> str:
        """Outputs a DEB822 representation of this source file
        
        Returns: str
            The DEB822-format representation of this source file
        """


    def output_ui() -> str:
        """Outputs a UI-friendly representation of this source file
        
        Returns: str
            This source formatted for screen output
        """


    def output() -> str:
        """Outputs the default format representation of this source file
        
        Returns: str
            This source formatted according to its set format
        """


    def load() -> None:
        """Loads the sources from the file"""


    def save() -> None:
        """Saves the source file to disk using the current format"""
