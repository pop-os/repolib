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

import unittest

from .. import file, util, source

class SourceTestCase(unittest.TestCase):
    def setUp(self): 
        util.set_testing()
        self.source = source.Source()
        self.source.ident = 'test'
        self.source.name = 'Test Source'
        self.source.enabled = True
        self.source.types = [util.SourceType.BINARY, util.SourceType.SOURCECODE]
        self.source.uris = ['http://example.com/ubuntu', 'http://example.com/mirror']
        self.source.suites = ['suite', 'suite-updates']
        self.source.components = ['main', 'contrib', 'nonfree']
        self.source.architectures = 'amd64 armel'
        self.source.languages = 'en_US en_CA'
        self.file = file.SourceFile(name=self.source.ident)
        self.file.add_source(self.source)
        self.source.file = self.file

        self.source_legacy = source.Source()
        self.source_legacy.ident = 'test-legacy'
        self.source_legacy.name = 'Test Legacy Source'
        self.source_legacy.enabled = True
        self.source_legacy.types = [util.SourceType.BINARY]
        self.source_legacy.uris = ['http://example.com/ubuntu']
        self.source_legacy.suites = ['suite']
        self.source_legacy.components = ['main', 'contrib', 'nonfree']
        self.source_legacy.architectures = 'amd64 armel'
        self.source_legacy.languages = 'en_US en_CA'
        self.source_legacy.file = file.SourceFile(name=self.source_legacy.ident)
        self.source_legacy.file.format = util.SourceFormat.LEGACY
        

    def test_default_source_data(self):
        self.assertEqual(self.source.name, 'Test Source')
        self.assertTrue(self.source.enabled.get_bool())
        self.assertEqual(
            self.source.types,
            [util.SourceType.BINARY, util.SourceType.SOURCECODE]
        )
        self.assertTrue(self.source.sourcecode_enabled)
        self.assertEqual(
            self.source.uris,
            ['http://example.com/ubuntu', 'http://example.com/mirror']
        )
        self.assertEqual(
            self.source.suites,
            ['suite', 'suite-updates']
        )
        self.assertEqual(
            self.source.components,
            ['main', 'contrib', 'nonfree']
        )
        self.assertEqual(self.source.architectures, 'amd64 armel')
        self.assertEqual(self.source.languages, 'en_US en_CA')
        self.assertEqual(self.source.file.path.name, 'test.sources')
    
    def test_output_822(self):
        source_string = (
            'X-Repolib-ID: test\n'
            'X-Repolib-Name: Test Source\n'
            'Enabled: yes\n'
            'Types: deb deb-src\n'
            'URIs: http://example.com/ubuntu http://example.com/mirror\n'
            'Suites: suite suite-updates\n'
            'Components: main contrib nonfree\n'
            'Architectures: amd64 armel\n'
            'Languages: en_US en_CA\n'
        )
        legacy_source_string = (
            'X-Repolib-ID: test-legacy\n'
            'X-Repolib-Name: Test Legacy Source\n'
            'Enabled: yes\n'
            'Types: deb\n'
            'URIs: http://example.com/ubuntu\n'
            'Suites: suite\n'
            'Components: main contrib nonfree\n'
            'Architectures: amd64 armel\n'
            'Languages: en_US en_CA\n'
        )
        self.assertEqual(self.source.deb822, source_string)
        self.assertEqual(self.source_legacy.deb822, legacy_source_string)
    
    def test_output_ui(self):
        source_string = (
            'test:\n'
            'Name: Test Source\n'
            'Enabled: yes\n'
            'Types: deb deb-src\n'
            'URIs: http://example.com/ubuntu http://example.com/mirror\n'
            'Suites: suite suite-updates\n'
            'Components: main contrib nonfree\n'
            'Architectures: amd64 armel\n'
            'Languages: en_US en_CA\n'
            ''
        )
        legacy_source_string = (
            'test-legacy:\n'
            'Name: Test Legacy Source\n'
            'Enabled: yes\n'
            'Types: deb\n'
            'URIs: http://example.com/ubuntu\n'
            'Suites: suite\n'
            'Components: main contrib nonfree\n'
            'Architectures: amd64 armel\n'
            'Languages: en_US en_CA\n'
        )
        self.assertEqual(self.source.ui, source_string)
        self.assertEqual(self.source_legacy.ui, legacy_source_string)
    
    def test_output_legacy(self):
        source_string = (
            'deb [arch=amd64,armel lang=en_US,en_CA] http://example.com/ubuntu suite main contrib nonfree  ## X-Repolib-Name: Test Legacy Source # X-Repolib-ID: test-legacy'
        )
        self.assertEqual(self.source_legacy.legacy, source_string)

    def test_enabled(self):
        self.source.enabled = False
        self.assertFalse(self.source.enabled.get_bool())
    
    def test_sourcecode_enabled(self):
        self.source.sourcecode_enabled = False
        self.assertEqual(self.source.types, [util.SourceType.BINARY])
    
    def test_dict_access(self):
        self.assertEqual(self.source['X-Repolib-ID'], 'test')
        self.assertEqual(self.source['X-Repolib-Name'], 'Test Source')
        self.assertEqual(self.source['Enabled'], 'yes')
        self.assertEqual(self.source['Enabled'], 'yes')
        self.assertEqual(self.source['Types'], 'deb deb-src')
        self.assertEqual(self.source['URIs'], 'http://example.com/ubuntu http://example.com/mirror')
        self.assertEqual(self.source['Suites'], 'suite suite-updates')
        self.assertEqual(self.source['Components'], 'main contrib nonfree')
        self.assertEqual(self.source['Architectures'], 'amd64 armel')
        self.assertEqual(self.source['Languages'], 'en_US en_CA')
    
    def test_load(self):
        load_source = source.Source()
        load_source.load_from_data([
            'X-Repolib-ID: load-test',
            'X-Repolib-Name: Test Source Loading',
            'Enabled: yes',
            'Types: deb',
            'URIs: http://example.com/ubuntu http://example.com/mirror',
            'Suites: suite suite-updates',
            'Components: main contrib nonfree',
            'Architectures: amd64 armel',
            'Languages: en_US en_CA',
        ])

        self.assertEqual(load_source.ident, 'load-test')
        self.assertEqual(load_source.name, 'Test Source Loading')
        self.assertTrue(load_source.enabled.get_bool())
        self.assertEqual(
            load_source.types,
            [util.SourceType.BINARY]
        )
        self.assertEqual(
            load_source.uris,
            ['http://example.com/ubuntu', 'http://example.com/mirror']
        )
        self.assertEqual(
            load_source.suites,
            ['suite', 'suite-updates']
        )
        self.assertEqual(
            load_source.components,
            ['main', 'contrib', 'nonfree']
        )
        self.assertEqual(load_source.architectures, 'amd64 armel')
        self.assertEqual(load_source.languages, 'en_US en_CA')

        load_legacy_source = source.Source()
        load_legacy_source.load_from_data(
            ['deb [arch=amd64,armel lang=en_US,en_CA] http://example.com/ubuntu suite main contrib nonfree  ## X-Repolib-Name: Test Legacy Source Loading # X-Repolib-ID: test-load-legacy']
        )

        self.assertEqual(load_legacy_source.ident, 'test-load-legacy')
        self.assertEqual(load_legacy_source.name, 'Test Legacy Source Loading')
        self.assertTrue(load_legacy_source.enabled.get_bool())
        self.assertEqual(
            load_legacy_source.types,
            [util.SourceType.BINARY]
        )
        self.assertEqual(
            load_legacy_source.uris,
            ['http://example.com/ubuntu']
        )
        self.assertEqual(
            load_legacy_source.suites,
            ['suite']
        )
        self.assertEqual(
            load_legacy_source.components,
            ['main', 'contrib', 'nonfree']
        )
        self.assertEqual(load_legacy_source.architectures, 'amd64 armel')
        self.assertEqual(load_legacy_source.languages, 'en_US en_CA')

    def test_save_load(self):
        self.source.file.save()
        load_source_file = file.SourceFile(name='test')
        load_source_file.load()
        self.assertGreater(len(load_source_file.sources), 0)
        self.assertGreater(
            len(load_source_file.contents), len(load_source_file.sources)
        )
        load_source = load_source_file.sources[0]

        self.assertEqual(load_source.ident, self.source.ident)
        self.assertEqual(load_source.name, self.source.name)
        self.assertEqual(load_source.enabled, self.source.enabled)
        self.assertEqual(load_source.types, self.source.types)
        self.assertEqual(load_source.sourcecode_enabled, self.source.sourcecode_enabled)
        self.assertEqual(load_source.uris, self.source.uris)
        self.assertEqual(load_source.suites, self.source.suites)
        self.assertEqual(load_source.components, self.source.components)
        self.assertEqual(load_source.architectures, self.source.architectures)
        self.assertEqual(load_source.languages, self.source.languages)
        self.assertEqual(load_source.file.name, self.source.file.name)
        