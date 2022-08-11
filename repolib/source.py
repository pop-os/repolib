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
        id(str): The unique id for this source
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
        self.file = file
    
    def set_enabled(self, enabled:bool) -> None:
        """Sets this source to be enabled or disabled
        
        Arguments:
            enabled(bool): `True` to enable the source, `False` to disable it.
        """
    
    def generate_default_id() -> str:
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
