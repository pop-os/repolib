#!/usr/bin/python3

"""
Copyright (c) 2019-2020, Ian Santopietro
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
