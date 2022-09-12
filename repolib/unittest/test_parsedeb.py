#!/usr/bin/python3

"""
Copyright (c) 2019-2022, Ian Santopietro
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

import unittest

from ..source import Source
from .. import util

class DebTestCase(unittest.TestCase):
    def test_normal_source(self):
        source = Source()
        source.load_from_data([
            'deb http://example.com/ suite main'
        ])
        source.generate_default_ident()
        self.assertEqual(source.types, [util.SourceType.BINARY])
        self.assertTrue(source.enabled.get_bool())
        self.assertEqual(source.uris, ['http://example.com/'])
        self.assertEqual(source.suites, ['suite'])
        self.assertEqual(source.components, ['main'])
        self.assertEqual(source.ident, 'example-com-binary')

    def test_source_with_multiple_components(self):
        source = Source()
        source.load_from_data([
            'deb http://example.com/ suite main nonfree'
        ])
        source.generate_default_ident()
        self.assertEqual(source.suites, ['suite'])
        self.assertEqual(source.components, ['main', 'nonfree'])

    def test_source_with_option(self):
        source = Source()
        source.load_from_data([
            'deb [ arch=amd64 ] http://example.com/ suite main'
        ])
        source.generate_default_ident()
        self.assertEqual(source.uris, ['http://example.com/'])
        self.assertEqual(source.architectures, 'amd64')

    def test_source_uri_with_brackets(self):
        source = Source()
        source.load_from_data([
            'deb http://example.com/[release]/ubuntu suite main'
        ])
        source.generate_default_ident()
        self.assertEqual(source.uris, ['http://example.com/[release]/ubuntu'])

    def test_source_options_with_colons(self):
        source = Source()
        source.load_from_data([
            'deb [ arch=arm:2 ] http://example.com/ suite main'
        ])
        source.generate_default_ident()
        self.assertEqual(source.uris, ['http://example.com/'])
        self.assertEqual(source.architectures, 'arm:2')

    def test_source_with_multiple_option_values(self):
        source = Source()
        source.load_from_data([
            'deb [ arch=armel,amd64 ] http://example.com/ suite main'
        ])
        source.generate_default_ident()
        self.assertEqual(source.uris, ['http://example.com/'])
        self.assertEqual(source.architectures, 'armel amd64')

    def test_source_with_multiple_options(self):
        source = Source()
        source.load_from_data([
            'deb [ arch=amd64 lang=en_US ] http://example.com/ suite main'
        ])
        source.generate_default_ident()
        self.assertEqual(source.uris, ['http://example.com/'])
        self.assertEqual(source.architectures, 'amd64')
        self.assertEqual(source.languages, 'en_US')

    def test_source_with_multiple_options_with_multiple_values(self):
        source = Source()
        source.load_from_data([
            'deb [ arch=amd64,armel lang=en_US,en_CA ] '
            'http://example.com/ suite main'
        ])
        source.generate_default_ident()
        self.assertEqual(source.uris, ['http://example.com/'])
        self.assertEqual(source.architectures, 'amd64 armel')
        self.assertEqual(source.languages, 'en_US en_CA')

    def test_source_uri_with_brackets_and_options(self):
        source = Source()
        source.load_from_data([
            'deb [ arch=amd64 lang=en_US,en_CA ] '
            'http://example][.com/[release]/ubuntu suite main'
        ])
        source.generate_default_ident()
        self.assertEqual(source.uris, ['http://example][.com/[release]/ubuntu'])
        self.assertEqual(source.architectures, 'amd64')
        self.assertEqual(source.languages, 'en_US en_CA')
        
    def test_source_uri_with_brackets_and_options_with_colons(self):
        source = Source()
        source.load_from_data([
            'deb [ arch=amd64,arm:2 lang=en_US,en_CA ] '
            'http://example][.com/[release]/ubuntu suite main'
        ])
        source.generate_default_ident()
        self.assertEqual(source.uris, ['http://example][.com/[release]/ubuntu'])
        self.assertEqual(source.architectures, 'amd64 arm:2')
        self.assertEqual(source.languages, 'en_US en_CA')

    def test_worst_case_sourcenario(self):
        source = Source()
        source.load_from_data([
            'deb [ arch=amd64,arm:2,arm][ lang=en_US,en_CA ] '
            'http://example][.com/[release:good]/ubuntu suite main restricted '
            'nonfree not-a-component'
        ])
        source.generate_default_ident()
        self.assertEqual(source.uris, ['http://example][.com/[release:good]/ubuntu'])
        self.assertEqual(source.suites, ['suite'])
        self.assertEqual(source.components, [
            'main', 'restricted', 'nonfree', 'not-a-component'
        ])
        source.generate_default_ident()
        self.assertEqual(source.architectures, 'amd64 arm:2 arm][')
        self.assertEqual(source.languages, 'en_US en_CA')

    def test_source_code_source(self):
        source = Source()
        source.load_from_data([
            'deb-src http://example.com/ suite main'
        ])
        source.generate_default_ident()
        self.assertEqual(source.types, [util.SourceType.SOURCECODE])

    def test_disabled_source(self):
        source = Source()
        source.load_from_data([
            '# deb http://example.com/ suite main'
        ])
        source.generate_default_ident()
        self.assertFalse(source.enabled.get_bool())

    def test_disabled_source_without_space(self):
        source = Source()
        source.load_from_data([
            '#deb http://example.com/ suite main'
        ])
        source.generate_default_ident()
        self.assertFalse(source.enabled.get_bool())

    def test_source_with_trailing_comment(self):
        source = Source()
        source.load_from_data([
            'deb http://example.com/ suite main # This is a comment'
        ])
        source.generate_default_ident()
        self.assertEqual(source.suites, ['suite'])
        self.assertEqual(source.components, ['main'])

    def test_disabled_source_with_trailing_comment(self):
        source = Source()
        source.load_from_data([
            '# deb http://example.com/ suite main # This is a comment'
        ])
        source.generate_default_ident()
        self.assertEqual(source.suites, ['suite'])
        self.assertEqual(source.components, ['main'])
