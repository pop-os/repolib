#!/usr/bin/python3

"""
Copyright (c) 2019, Ian Santopietro
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
"""

import os

from . import util

class PPAError(Exception):
    pass

class Source():

    def __init__(self,
                 name='', enabled=True, types=[],
                 uris=[], suites=[], components=[], options={}, 
                 filename='example.source'):
        """
        Constructor for the Source class.

        Keyword Arguments:
          enabled -- Whether the source is enabled or disabled (default: True)
          types -- List of debian source repository types 
          uris -- List of URIs the source uses 
          suites -- List of suites for the source (e.g. disco) 
          components -- List of source components (e.g. main) 
          options -- Dict of options for the source. 
          filename -- The filename of the source file on disk (default: example.source)
        """
        self.name = name
        self.set_enabled(enabled)
        self.types = []
        for type in types:
            self.types.append(util.AptSourceType(type.strip()))
        self.uris = uris
        self.suites = suites
        self.components = components
        self.options = options
        self.filename = filename
    
    def make_name(self, prefix=''):
        uri = self.uris[0].replace('/', ' ')
        uri_list = uri.split()
        name = '{}{}.sources'.format(
            prefix,
            '-'.join(uri_list[1:]).translate(util.CLEAN_CHARS)
        )
        return name
    
    def load_from_file(self, filename=None):
        """
        Loads the source from a file on disk.

        Keyword arguments:
          filename -- STR, Containing the path to the file. (default: self.filename)
        """
        if filename:
            self.filename = filename
        self.enabled = util.AptSourceEnabled.TRUE
        self.types = []
        self.uris = []
        self.suites = []
        self.components = []
        self.options = {}

        full_path = os.path.join(util.sources_dir, self.filename)
        
        with open(full_path, 'r') as source_file:
            for line in source_file:
                line = line.strip()
                if line.startswith('X-Repolib-Name:'):
                    self.name = " ".join(line.split()[1:])
                elif line.startswith('Enabled:'):
                    self.enabled=util.AptSourceEnabled(line.split(":")[1].strip().lower())
                elif line.startswith('Types:'):
                    types = line.split(' ')
                    for type in types[1:]:
                        self.types.append(util.AptSourceType(type.strip()))
                elif line.startswith('URIs'):
                    uris = line.split(' ')
                    for uri in uris[1:]:
                        self.uris.append(uri.strip())
                elif line.startswith('Suites:'):
                    suites = line.split(' ')
                    for suite in suites[1:]:
                        self.suites.append(suite.strip())
                elif line.startswith('Components:'):
                    components = line.split(' ')
                    for component in components[1:]:
                        self.components.append(component.strip())
                elif line == "":
                    continue
                else:
                    option = line.replace(':', '').strip().split(' ')
                    self.options[option[0]] = option[1:]
                    
    
    def translate_options(self, option):
        """
        Translates an old-style option into a DEB822 option

        Arguments:
          option -- The option to check and translate
        
        Returns the translated option
        """
        translations = {
            'arch': 'Architectures',
            'lang': 'Languages',
            'target': 'Targets',
            'pdiffs': 'PDiffs',
            'by-hash': 'By-Hash'
        }
        if option in translations:
            option = translations[option]
        return option
    
    def save_to_disk(self):
        """ Saves the source to disk at self.filename location."""
        string_source = self.make_source_string()
        string_source = string_source.replace('Name: ', 'X-Repolib-Name: ')
        full_path = os.path.join(util.sources_dir, self.filename)

        with open(full_path, 'w') as source_file:
            source_file.write(string_source)
    
    def make_source_string(self):
        """Makes a string of the source."""
        if self.name == '':
            self.name = self.filename.replace('.sources', '')
            
        toprint  = "Name: {}\n".format(self.name)
        toprint += "Enabled: {}\n".format(self.enabled.value) 
        toprint += "Types: {}\n".format(" ".join(self.get_types())) 
        toprint += "URIs: {}\n".format(" ".join(self.uris)) 
        toprint += "Suites: {}\n".format(" ".join(self.suites)) 
        toprint += "Components: {}\n".format(" ".join(self.components)) 
        toprint += "{}".format(self.get_options())
        return toprint
    
    def set_enabled(self, is_enabled):
        """
        Sets whether the source should be enabled or disabled.

        Positional Arguments:
          is_enabled -- BOOL, the desired state of the source
        """
        enable = {
            True : util.AptSourceEnabled.TRUE,
            False: util.AptSourceEnabled.FALSE
        }
        self.enabled = enable[is_enabled]
    
    def set_source_enabled(self, is_enabled):
        if is_enabled:
            self.types = [
                util.AptSourceType.BINARY,
                util.AptSourceType.SOURCE
            ]
        else:
            self.types = [util.AptSourceType.BINARY]

    def get_options(self):
        opt_str = ''
        for key in self.options:
            opt_str += '{key}: {values}\n'.format(key=key, values=' '.join(self.options[key]))
        return opt_str
    
    def get_types(self):
        types_s = []
        for i in self.types:
            types_s.append(i.value)
        return types_s

class SystemSource(Source):

    def __init__(self,
                 enabled=True, types=[],
                 uris=[''], suites=[''], components=[''], options={}, 
                 filename='system.sources'):
        super().__init__(filename=filename)
        self.load_from_file()