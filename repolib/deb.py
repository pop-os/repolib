#!/usr/bin/python3

"""
Copyright (c) 2019-2020, Ian Santopietro
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

This is a library for parsing deb lines into deb822-format data.
"""

import re

from . import source
from . import util

options_re = re.compile(r'[^@.+]\[([^[]+.+)\]\ ')
uri_re = re.compile(r'\w+:(\/?\/?)[^\s]+')

class DebLine(source.Source):

    outoptions_d = {
        'Architectures': 'arch',
        'Languages': 'lang',
        'Targets': 'target',
        'PDiffs': 'pdiffs',
        'By-Hash': 'by-hash'
    }
    
    def __init__(self, line):
        super().__init__()
        # Clean up deb line by making spaces consistent 
        self.name = ''
        self.enabled = util.AptSourceEnabled.TRUE
        self.types = []
        self.uris = []
        self.suites = []
        self.components = []
        self.options = {}
        
        self.deb_line = line
        if 'cdrom:' in self.deb_line:
            raise util.RepoError(
                'RepoLib does not support \'cdrom:\' URIs via this DebLine Class. '
                'Please use a Source() class to add these sources'
            )
        self._parse_debline(self.deb_line)
        self.filename = self._make_name(prefix="deb-")
        self.name = self.filename.replace('.sources', '')
        
    
    def _make_name(self, prefix=''):
        uri = self.uris[0].replace('/', ' ')
        uri_list = uri.split()
        name = '{}{}.sources'.format(
            prefix,
            '-'.join(uri_list[1:]).translate(util.CLEAN_CHARS)
        )
        return name
    
    def _make_debline(self):
        line = ''

        if len(self.uris) > 1 or len(self.suites) > 1:
            return False
        
        if self.enabled == util.AptSourceEnabled.FALSE:
            line += '# '
        
        line += f'{self.types[0].get_string()} '
        
        if self.options:
            line += '['
            line += self._get_options()
            line = line.strip()
            line += '] '

        line += f'{self.uris[0]} '
        line += f'{self.suites[0]} '
        
        for component in self.components:
            line += f'{component} '
        
        return line.strip()

    def _parse_debline(self, line):
        # Enabled vs. Disabled
        if line.startswith('#'):
            self.set_enabled(False)
            line = line.replace('#', '', 1)
            line = line.strip()
        
        # URI parsing
        for uri in uri_re.finditer(line):
            self.uris = [uri[0]]
            line_uri = line.replace(uri[0], '')
        
        # Options parsing
        try:
            options = options_re.search(line_uri).group()
            self._set_options(options.strip())
            line_uri = line_uri.replace(options, '')
        except AttributeError:
            pass
        
        deb_list = line_uri.split()
        
        # Type Parsing
        self.types = [util.AptSourceType.BINARY]
        if deb_list[0] == 'deb-src':
            self.types = [util.AptSourceType.SOURCE]

        # Suite Parsing
        self.suites = [deb_list[1]]

        # Components parsing
        for item in deb_list[2:]:
            if not item.startswith('#'):
                self.components.append(item)
            else:
                break
    
    def _validate(self, valid):
        """
        Ensure we have a valid debian repository line.
        """
        if valid.startswith('#'):
            self.set_enabled(False)
            valid = valid.replace('#', '')
        valid = valid.strip()
        if not valid.startswith('deb'):
            raise util.RepoError(
                'The line %s does not appear to be a valid repo' % self.deb_line
            )
    
    def _get_options(self):
        opt_str = ''
        for key in self.options:
            opt_str += '{key}={values} '.format(key=self.outoptions_d[key], values=','.join(self.options[key]))
        return opt_str

    def _set_type(self, deb_type):
        """
        Set the type of repository (deb or deb-src)
        """
        self.types = [util.AptSourceType(deb_type)]
    
    def _set_options(self, options):
        """
        Set the options.
        """
        # Split the option string into a list of chars, so that we can replace
        # the first and last characters ([ and ]) with spaces.
        op = list(options)
        op[0] = " "
        op[-1] = " "
        options = "".join(op).strip()
        
        for replacement in self.options_d:
                options = options.replace(replacement, self.options_d[replacement])
        
        options = options.replace('=', ',')
        options_list = options.split()
        
        for i in options_list:
            option = i.split(',')
            values_list = []
            for value in option[1:]:
                values_list.append(value)
            self.options[option[0]] = values_list
            