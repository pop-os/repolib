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

This is a library for parsing deb lines into deb822-format data.
"""

from . import source
from . import util

class DebLine(source.Source):

    options_d = {
        'arch': 'Architectures',
        'lang': 'Languages',
        'target': 'Targets',
        'pdiffs': 'PDiffs',
        'by-hash': 'By-Hash'
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
        deb_list = self.parse_debline(self.deb_line)

        self.validate(deb_list[0])

        if len(deb_list) == 1:
            ex_deb_list = deb_list[0].split()
            self.set_type(ex_deb_list[0])
            self.set_uris(ex_deb_list[1])
            self.set_suites(ex_deb_list[2])
            self.set_comps(ex_deb_list[3:])
            self.options = {}
        else: 
            self.set_type(deb_list[0])
            ex_deb_list = deb_list[2].split()
            self.set_uris(ex_deb_list[0])
            self.set_suites(ex_deb_list[1])
            self.set_comps(ex_deb_list[2:])
            self.set_options(deb_list[1])
        
        self.filename = self.make_name(prefix="deb-")

    def parse_debline(self, line):
        line = line.replace(']', '[')
        line = line.split('[')
        deb_list = []
        for i in line:
            deb_list.append(i.strip())
        return deb_list
    
    def validate(self, valid):
        """
        Ensure we have a valid debian repositor line.
        """
        if not valid.startswith('deb'):
            raise util.RepoError(
                'The line %s does not appear to be a valid repo' % self.deb_line
            )

    def set_type(self, deb_type):
        """
        Set the type of repository (deb or deb-src)
        """
        self.types = [util.AptSourceType(deb_type)]
    
    def set_uris(self, uri):
        """ 
        Set the URIs of the repository.
        """
        self.uris.append(uri)
    
    def set_suites(self, suite):
        """
        Sets the suite of the repository.

        Since single-line repos can only define a single suite, we're only going
        to apply our single one. Additional suites can be defined afterward.
        """
        self.suites.append(suite)
    
    def set_comps(self, comp_list):
        """
        Sets the components of the repository.

        Since single-line repos may specify multiple componentss, we need to iterate 
        through a list of provided comps and add each one.
        """        
        for comp in comp_list:
            self.components.append(comp)

    def set_options(self, options_str):
        """
        Set the options.
        """
        
        for replacement in self.options_d:
                options_str = options_str.replace(replacement, self.options_d[replacement])
        
        options_str = options_str.replace('=', ',')
        options_list = options_str.split()
        
        for i in options_list:
            option = i.split(',')
            values_list = []
            for value in option[1:]:
                values_list.append(value)
            self.options[option[0]] = values_list
            