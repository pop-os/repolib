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
"""
# pylint: disable=missing-function-docstring, missing-class-docstring
# These aren't really relevant for unit testing (which is mostly automatic.)

import unittest

from . import legacy_deb
from . import util


class LegacyTestCase(unittest.TestCase):

    def setUp(self):
        with open(util.get_sources_dir(testing=True) / 'test.list', mode='w') as test_file:
            test_file.write(
                'deb [arch=amd64] https://example.com ubuntu main universe\n'
                'deb-src [arch=amd64] https://example.com ubuntu main universe\n'
            )
        with open(util.get_sources_dir(testing=True) / 'test2.list', mode='w') as test_file:
            test_file.write(
                '## Added/managed by repolib ##\n'
                '#\n'
                '## X-Repolib-Name: example-com\n'
                'deb [arch=armel,amd64 lang=en_US] http://example.com ubuntu main\n'
                'deb-src [arch=armel,amd64 lang=en_US] http://example.com ubuntu main\n'
            )
        with open(util.get_sources_dir(testing=True) / 'test3.list', mode='w') as test_file:
            test_file.write(
                '## Added/managed by repolib ##\n'
                '#\n'
                '## X-Repolib-Name: test no suites\n'
                'deb [trusted=yes] file:///var/cache/apt/archives ./\n'
                'deb-src [trusted=yes] file:///var/cache/apt/archives ./\n'
            )
        self.source = legacy_deb.LegacyDebSource(ident='test')
        self.source.load_from_file()

    def test_no_suites(self):
        opts = {'Trusted': 'yes'}
        types = [util.AptSourceType.BINARY, util.AptSourceType.SOURCE]
        source = legacy_deb.LegacyDebSource(ident='test3')
        source.load_from_file()

        self.assertEqual(source.ident, 'test3')
        self.assertEqual(source.name, 'test no suites')
        self.assertEqual(source.types, types)
        self.assertEqual(source.uris, ['file:///var/cache/apt/archives'])
        self.assertEqual(source.suites, ['./'])
        self.assertFalse(source.components)
        self.assertDictEqual(source.options, opts)

    def test_load_from_file(self):
        opts = {'Architectures': 'amd64'}
        self.assertEqual(self.source.filename, 'test.list')
        self.assertEqual(len(self.source.sources), 2)
        for debsource in self.source.sources:
            self.assertEqual(len(debsource.types), 1)
            self.assertEqual(debsource.uris, ['https://example.com'])
            self.assertDictEqual(debsource.options, opts)
            self.assertEqual(debsource.suites, ['ubuntu'])
            self.assertEqual(debsource.components, ['main', 'universe'])

    def test_make_deblines(self):
        # pylint: disable=line-too-long
        # unittest doesn't like when this is split to a sane length. We need to
        # have it on one ugly line so that the assertion is Equal.
        expected = '## Added/managed by repolib ##\n#\n## X-Repolib-Name: example-com\ndeb [arch=amd64] https://example.com ubuntu main universe\ndeb-src [arch=amd64] https://example.com ubuntu main universe\n'
        actual = self.source.make_deblines()
        self.assertEqual(actual, expected)

    def test_validate(self):
        testline1 = '# deb http://example.com ubuntu main'
        testline2 = 'deb http://example.com ubuntu main'
        testline3 = '#deb-src http://example.com ubuntu main'
        testline4 = 'deb-src http://example.com ubuntu main'
        testline5 = '# dbe http://example.com ubuntu main'
        testline6 = 'dba http://example.com ubuntu main'
        testline7 = 'deb file:///var/cache/apt/archives ./'
        testline8 = 'deb [trusted=yes] file:///var/cache/apt/archives ./'

        for line in [testline1, testline2, testline3, testline4, testline7, testline8]:
            self.assertTrue(util.validate_debline(line))

        for line in [testline5, testline6]:
            self.assertFalse(util.validate_debline(line))

    def test_save_to_disk(self):
        with open(util.get_sources_dir(testing=True) / 'test2.list', mode='r') as expected_file:
            expected_data = expected_file.readlines()

        with open(util.get_sources_dir(testing=True) / 'test.list', mode='r') as source_file:
            source_data = source_file.readlines()
        self.assertNotEqual(source_data, expected_data)

        self.source.uris = ['http://example.com']
        self.source.options = {
            'Architectures': 'armel amd64',
            'Languages': 'en_US'
        }
        self.source.components = ['main']
        self.source.filename = 'test3.list'
        self.source.save_to_disk()

        with open(util.get_sources_dir(testing=True) / 'test3.list', mode='r') as source_file:
            source_file.seek(0)
            source_data = source_file.readlines()
        self.assertEqual(source_data, expected_data)
