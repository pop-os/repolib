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

from . import util

log = logging.getLogger(__name__)

class DebParseError(util.RepoError):
    """ Exceptions related to parsing deb lines."""

    def __init__(self, *args, code=1, **kwargs):
        """Exceptions related to parsing deb lines.

        Arguments:
            code (:obj:`int`, optional, default=1): Exception error code.
    """
        super().__init__(*args, **kwargs)
        self.code = code

def debsplit(line:str) -> list:
    """ Improved string.split() with support for things like [] options. 
    
    Adapted from python-apt

    Arguments:
        line(str): The line to split up.
    """
    line = line.strip()
    line_list = line.split()
    for i in line_list:
        if util.url_validator(i):
            line_list[line_list.index(i)] = decode_brackets(i)
    line = ' '.join(line_list)
    pieces:list = []
    tmp:str = ""
    # we are inside a [..] block
    p_found = False
    for char in line:
        if char == '[':
            p_found = True
            tmp += char
        elif char == ']':
            p_found = False
            tmp += char
        elif char.isspace() and not p_found:
            pieces.append(tmp)
            tmp = ''
            continue
        else:
            tmp += char
    # append last piece
    if len(tmp) > 0:
        pieces.append(tmp)
    return pieces

def encode_brackets(word:str) -> str:
    """ Encodes any [ and ] brackets into URL-safe form

    Technically we should never be recieving these, and there are other things 
    which should technically be encoded as well. However, square brackets 
    actively break the URL parsing, and must be strictly avoided.

    Arguments:
        word (str): the string to encode brackets in.
    
    Returns:
        `str`: the encoded string.
    """
    word = word.replace('[', '%5B')
    word = word.replace(']', '%5D')
    return word

def decode_brackets(word:str) -> str:
    """ Un-encodes [ and ] from the input

    Since our downstream libraries should also be encoding these correctly, it 
    is better to retain these as the user entered, as that ensures they can 
    recognize it properly.

    Arguments:
        word (str): The string to decode.

    Returns:
        `str`: the decoded string.
    """
    word = word.replace('%5B', '[')
    word = word.replace('%5D', ']')
    return word

def parse_name_ident(tail:str) -> tuple:
    """ Find a Repolib name within the given comment string.

    The name should be headed with "X-Repolib-Name:" and is not space terminated.
    The ident should be headed with "X-Repolib-ID:" and is space terminated.

    Either field ends at the end of a line, or at a subsequent definition of a
    different field, or at a subsequent ' #' substring. Additionally, the ident
    field ends with a subsequent space.

    Arguments:
        tail (str): The comment to search within.
    
    Returns: tuple(name, ident, comment):
        name (str): The detected name, or None
        ident (str): The detected ident, or None
        comment (str): The string with the name and ident removed
    """
    tail = util.strip_hashes(tail)

    # Used for sanity checking later
    has_name = 'X-Repolib-Name' in tail
    log.debug('Line name found: %s', has_name)
    has_ident = 'X-Repolib-ID' in tail
    log.debug('Line ident found: %s', has_ident)

    parts: list = tail.split()
    name_found = False
    ident_found = False
    name:str = ''
    ident:str = ''
    comment:str = ''
    for item in parts:
        log.debug("Checking line item: %s", item)
        item_is_name = item.strip('#').strip().startswith('X-Repolib-Name')
        item_is_ident = item.strip('#').strip().startswith('X-Repolib-ID')
        
        if '#' in item and not item_is_name and not item_is_ident:
            name_found = False
            ident_found = False
        
        elif item_is_name:
            name_found = True
            ident_found = False
            continue
        
        elif item_is_ident:
            name_found = False
            ident_found = True
            continue
        
        if name_found and not item_is_name:
            name += f'{item} '
            continue
        
        elif ident_found and not item_is_ident:
            ident += f'{item}'
            ident_found = False
            continue
        
        elif not name_found and not ident_found:
            c = item.strip('#')
            comment += f'{c} '

    name = name.strip()
    ident = ident.strip()
    comment = comment.strip()

    if not name:
        if ident: 
            name = ident

    # Final sanity checking
    if has_name and not name:
        raise DebParseError(
            f'Could not parse repository name from comment {comment}. Make sure '
            'you have a space between the colon and the Name'
        )
    if has_ident and not ident:
        raise DebParseError(
            f'Could not parse repository ident from comment {comment}. Make sure '
            'you have a space between the colon and the Ident'
        )

    return name, ident, comment


class ParseDeb:
    """ Parsing for source entries. 

    Contains parsing helpers for one-line format sources.
    """

    def __init__(self, debug:bool = False) -> None:
        """
        Arguments:
            debug (bool): In debug mode, the structured data is always returned
                at the end, instead of checking for sanity (default: `False`)
        """
        self.debug = debug
        self.last_line: str = ''
        self.last_line_valid: bool = False
        self.curr_line: str = ''
        self.curr_line_valid: bool = False
    
    def parse_options(self, opt:str) -> dict:
        """ Parses a string of options into a dictionary that repolib can use.

        Arguments:
            opt(str): The string with options returned from the line parser.
        
        Returns:
            `dict`: The dictionary of options with key:val pairs (may be {})
        """
        opt = opt.strip()
        opt = opt[1:-1].strip() # Remove enclosing brackets
        options = opt.split()

        parsed_options:dict = {}

        for opt in options:
            pre_key, values = opt.split('=')
            values = values.split(',')
            value:str = ' '.join(values)
            try:
                key:str = util.options_inmap[pre_key]
            except KeyError:
                raise DebParseError(
                    f'Could not parse line {self.curr_line}: option {opt} is '
                    'not a valid debian repository option or is unsupported.'
                )
            parsed_options[key] = value
        
        return parsed_options

    
    def parse_line(self, line:str) -> dict:
        """ Parse a deb line into its individual parts.

        Adapted from python-apt

        Arguments:
            line (str): The line input to parse
        
        Returns:
            (dict): a dict containing the requisite data.
        """
        self.last_line = self.curr_line
        self.last_line_valid = self.curr_line_valid
        self.curr_line = line.strip()
        parts:list = []

        line_is_comment = self.curr_line == '#'
        line_is_empty = self.curr_line == ''
        if line_is_comment or line_is_empty:
            raise DebParseError(f'Current line "{self.curr_line}" is empty')
        
        line_parsed: dict = {}
        line_parsed['enabled'] = True
        line_parsed['name'] = ''
        line_parsed['ident'] = ''
        line_parsed['comments'] = []
        line_parsed['repo_type'] = ''
        line_parsed['uri'] = ''
        line_parsed['suite'] = ''
        line_parsed['components'] = []
        line_parsed['options'] = {}
        
        if line.startswith('#'):
            line_parsed['enabled'] = False
            line = util.strip_hashes(line)
            parts = line.split()
            if not parts[0] in ('deb', 'deb-src'):
                raise DebParseError(f'Current line "{self.curr_line}" is invalid')
        
        comments_index = line.find('#')
        if comments_index > 0:
            raw_comments:str = line[comments_index + 1:].strip()
            (
                line_parsed['name'],
                line_parsed['ident'],
                comments
            ) = parse_name_ident(raw_comments)
            line_parsed['comments'].append(comments)
            line = line[:comments_index]
        
        parts = debsplit(line)
        if len(parts) < 3: # We need at least a type, a URL, and a component
            raise DebParseError(
                f'The line "{self.curr_line}" does not have enough pieces to be'
                'valid'
            )
        # Determine the type of the repo
        repo_type:str = parts.pop(0)
        if repo_type in ['deb', 'deb-src']:
            line_parsed['repo_type'] = util.SourceType(repo_type)
        else:
            raise DebParseError(f'The line "{self.curr_line}" is of invalid type.')

        # Determine the properties of our repo line
        uri_index:int = 0
        is_cdrom: bool = False
        ## The URI index is the vital piece of information we need to parse the 
        ## deb line, as it's position determines what other components are 
        ## present and where they are. This determines the location of the URI
        ## regardless of where it's at.
        for part in parts:
            if part.startswith('['):
                if 'cdrom' in part:
                    is_cdrom = True
                    uri_index = parts.index(part)
                else:
                    uri_index = 1
        
        if is_cdrom:
            # This could maybe change if the parser now differentiates between 
            # CDROM URIs and option lists
            raise DebParseError('Repolib cannot currently accept CDROM Sources')

        if uri_index != 0:
            line_parsed['options'] = self.parse_options(parts.pop(0))
        
        if len(line_parsed) < 2: # Should have at minimum a URI and a suite/path
            raise DebParseError(
                f'The line "{self.curr_line}" does not have enough pieces to be'
                'valid'
            )
        
        line_uri = parts.pop(0)
        if util.url_validator(line_uri):
            line_parsed['uri'] = line_uri
        
        else:
            raise DebParseError(
                f'The line "{self.curr_line}" has invalid URI: {line_uri}'
            )

        line_parsed['suite'] = parts.pop(0)
        
        line_components:list = []
        for comp in parts:
            line_parsed['components'].append(comp)
        
        
        has_type = line_parsed['repo_type']
        has_uri = line_parsed['uri']
        has_suite = line_parsed['suite']

        if has_type and has_uri and has_suite:
            # if we have these three minimum components, we can proceed and the
            # line is valid. Otherwise, error out.
            return line_parsed.copy()
        
        if self.debug:
            return line_parsed.copy()
        
        raise DebParseError(
            f'The line {self.curr_line} could not be parsed due to an '
            'unknown error (Probably missing the repo type, URI, or a '
            'suite/path).'
        )
