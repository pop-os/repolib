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

from . import source
from . import util

class SourceTestCase(unittest.TestCase):
    def setUp(self):
        self.source = source.Source(ident='test')
        self.source.name = 'Test Source'
        self.source.enabled = False
        self.source.types = [util.AptSourceType.BINARY, util.AptSourceType.SOURCE]
        self.source.uris = ['http://example.com/ubuntu', 'http://example.com/mirror']
        self.source.suites = ['suite', 'suite-updates']
        self.source.components = ['main', 'contrib', 'nonfree']
        self.source.options = {
            'Architectures': 'amd64 armel',
            'Languages': 'en_US en_CA'
        }

    def test_default_source_data(self):
        self.assertEqual(self.source.name, 'Test Source')
        # pylint: disable=no-member
        # This works fine, so I think pylint is just confused.
        self.assertFalse(self.source.enabled.get_bool())
        self.assertEqual(self.source.types, [
            util.AptSourceType.BINARY, util.AptSourceType.SOURCE
        ])
        self.assertEqual(self.source.uris, [
            'http://example.com/ubuntu', 'http://example.com/mirror'
        ])
        self.assertEqual(self.source.suites, [
            'suite', 'suite-updates'
        ])
        self.assertEqual(self.source.components, [
            'main', 'contrib', 'nonfree'
        ])
        self.assertDictEqual(self.source.options, {
            'Architectures': 'amd64 armel',
            'Languages': 'en_US en_CA'
        })
        self.assertEqual(self.source.filename, 'test.sources')

    def test_make_source_string(self):
        source_string = (
            'Name: Test Source\n'
            'Enabled: no\n'
            'Types: deb deb-src\n'
            'URIs: http://example.com/ubuntu http://example.com/mirror\n'
            'Suites: suite suite-updates\n'
            'Components: main contrib nonfree\n'
            'Architectures: amd64 armel\n'
            'Languages: en_US en_CA\n'
        )
        self.assertEqual(self.source.make_source_string(), source_string)

    def test_set_enabled(self):
        self.source.enabled = True
        # pylint: disable=no-member
        # This works fine, so I think pylint is just confused.
        self.assertTrue(self.source.enabled.get_bool())

    def test_set_source_enabled(self):
        self.source.set_source_enabled(False)
        self.assertEqual(self.source.types, [util.AptSourceType.BINARY])
