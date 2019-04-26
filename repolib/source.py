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

from . import util, ppa

class PPAError(Exception):
    pass

class Source():

    def __init__(self,
                 enabled=True, types=[],
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
        self.set_enabled(enabled)
        self.types = []
        for type in types:
            self.types.append(util.AptSourceType(type.strip()))
        self.uris = uris
        self.suites = suites
        self.components = components
        self.options = options
        self.filename = filename
    
    def load_from_ppa(self, ppa_line):
        self.enabled = util.AptSourceEnabled.TRUE
        self.types = []
        self.uris = []
        self.suites = []
        self.components = []
        self.options = {}
        self.ppa_line = ppa_line

        try:
            import lsb_release
        except ImportError:
            raise PPAError("The system can't find version information!")
        if not ppa_line.startswith('ppa:'):
            raise PPAError("The PPA %s is malformed!" % ppa_line)
        
        ppa_info = ppa_line.split(":")
        ppa_uri = 'http://ppa.launchpad.net/{}/ubuntu'.format(ppa_info[1])
        self.set_source_enabled(False)
        self.uris.append(ppa_uri)
        self.suites.append(lsb_release.get_distro_information()['CODENAME'])
        self.components.append('main')
        ppa_name = ppa_info[1].split('/')
        name = 'ppa-{}'.format('-'.join(ppa_name))
        self.filename = '{}.sources'.format(name)
    
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
                if line.startswith('Enabled:'):
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
                    option = line.strip().split(' ')
                    if option != "":
                        option_key = self.translate_options(option[0].strip(': '))
                        self.options[option_key] = option[1].strip()
    
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
        full_path = os.path.join(util.sources_dir, self.filename)

        with open(full_path, 'w') as source_file:
            source_file.write(string_source)
        
    def get_ppa_key(self):
        if self.ppa_line:
            ppa.add_key(self.ppa_line)
    
    def make_source_string(self):
        """Makes a string of the source."""
        toprint = (
                "Enabled: {}\n".format(self.enabled.value) + 
                "Types: {}\n".format(" ".join(self.cat_types())) +
                "URIs: {}\n".format(" ".join(self.uris)) +
                "Suites: {}\n".format(" ".join(self.suites)) +
                "Components: {}\n".format(" ".join(self.components)) +
                "{}".format("\n".join(self.cat_options())) + '\n'
        )
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

    def cat_options(self):
        opts_s = []
        for key in self.options:
            opts_s.append("{}: {}".format(key, self.options[key]))
        return opts_s
    
    def cat_types(self):
        types_s = []
        for i in self.types:
            types_s.append(i.value)
        return types_s

class SystemSource(Source):

    def __init__(self,
                 enabled=True, types=[],
                 uris=[''], suites=[''], components=[''], options={}, 
                 filename='00-system.sources'):
        super().__init__(filename=filename)
        self.load_from_file()