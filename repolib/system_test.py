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
# pylint: disable=missing-function-docstring, missing-class-docstring
# These aren't really relevant for unit testing (which is mostly automatic.)

import unittest

from . import system
from . import util

class SystemTestCase(unittest.TestCase):
    #pylint: disable=invalid-name
    # We're inheriting from unittest in this case.
    sources_dir = util.get_sources_dir(testing=True)

    def setUpModule(self):
        with open(self.sources_dir / 'modified_system.sources', mode='w') as sources_file:
            sources_file.write(
                'X-Repolib_Name: Pop!_OS Sources\n'
                'Enabled: no\n'
                'Types: deb\n'
                'URIs: http://apt.pop-os.org/ubuntu http://archive.ubuntu.com/ubuntu\n'
                'Suites: focal focal-updates focal-test\n'
                'Components: main universe multiverse test\n'
            )

    def setUp(self):
        with open(self.sources_dir / 'system.sources', mode='w') as sources_file:
            sources_file.write(
                'X-Repolib_Name: Pop!_OS Sources\n'
                'Enabled: no\n'
                'Types: deb deb-src\n'
                'URIs: http://apt.pop-os.org/ubuntu\n'
                'Suites: focal focal-updates focal-backports\n'
                'Components: main universe multiverse restricted\n'
            )
        self.source = system.SystemSource()

    def test_load_system_source(self):
        self.assertEqual(self.source.filename, 'system.sources')
        self.assertNotEqual(self.source.uris, [])
        self.assertNotEqual(self.source.suites, [])
        self.assertNotEqual(self.source.components, [])
        self.assertNotEqual(self.source.types, [])

    def test_set_component_enabled(self):
        expected = ['main', 'universe', 'multiverse', 'test']
        self.source.set_component_enabled(component='test')
        self.source.set_component_enabled(component='restricted', enabled=False)

        self.assertEqual(self.source.components, expected)

    def test_set_suite_enabled(self):
        expected = ['focal', 'focal-updates', 'focal-test']
        self.source.set_suite_enabled(suite='focal-backports', enabled=False)
        self.source.set_suite_enabled(suite='focal-test')

        self.assertEqual(self.source.suites, expected)

    def test_set_source_enabled(self):
        expected = [util.AptSourceType.BINARY]
        self.source.set_source_enabled(False)

        self.assertEqual(self.source.types, expected)
