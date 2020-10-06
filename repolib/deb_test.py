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

from . import deb
from . import util

class DebTestCase(unittest.TestCase):
    def test_normal_source(self):
        source = deb.DebLine(
            'deb http://example.com/ suite main'
        )
        self.assertEqual(source.name, 'deb-example-com')
        self.assertEqual(source.types, [util.AptSourceType.BINARY])
        # pylint: disable=no-member
        # This works fine, so I think pylint is just confused.
        self.assertTrue(source.enabled.get_bool())
        # pylint: enable=no-member
        self.assertEqual(source.uris, ['http://example.com/'])
        self.assertEqual(source.suites, ['suite'])
        self.assertEqual(source.components, ['main'])
        self.assertFalse(source.options)
        self.assertEqual(source.ident, 'deb-example-com')

    def test_source_with_multiple_components(self):
        source = deb.DebLine(
            'deb http://example.com/ suite main nonfree'
        )
        self.assertEqual(source.suites, ['suite'])
        self.assertEqual(source.components, ['main', 'nonfree'])

    def test_source_with_option(self):
        source = deb.DebLine(
            'deb [ arch=amd64 ] http://example.com/ suite main'
        )
        self.assertEqual(source.uris, ['http://example.com/'])
        self.assertDictEqual(source.options, {'Architectures': 'amd64'})

    def test_source_uri_with_brackets(self):
        source = deb.DebLine(
            'deb http://example.com/[release]/ubuntu suite main'
        )
        self.assertEqual(source.uris, ['http://example.com/[release]/ubuntu'])
        self.assertFalse(source.options, {})

    def test_source_options_with_colons(self):
        source = deb.DebLine(
            'deb [ arch=arm:2 ] http://example.com/ suite main'
        )
        self.assertEqual(source.uris, ['http://example.com/'])
        self.assertDictEqual(source.options, {'Architectures': 'arm:2'})

    def test_source_with_multiple_option_values(self):
        source = deb.DebLine(
            'deb [ arch=armel,amd64 ] http://example.com/ suite main'
        )
        self.assertEqual(source.uris, ['http://example.com/'])
        self.assertDictEqual(source.options, {'Architectures': 'armel amd64'})

    def test_source_with_multiple_options(self):
        source = deb.DebLine(
            'deb [ arch=amd64 lang=en_US ] http://example.com/ suite main'
        )
        self.assertEqual(source.uris, ['http://example.com/'])
        self.assertDictEqual(
            source.options,
            {'Architectures': 'amd64', 'Languages': 'en_US'}
        )

    def test_source_with_multiple_options_with_multiple_values(self):
        source = deb.DebLine(
            'deb [ arch=amd64,armel lang=en_US,en_CA ] '
            'http://example.com/ suite main'
        )
        self.assertEqual(source.uris, ['http://example.com/'])
        self.assertDictEqual(
            source.options,
            {'Architectures': 'amd64 armel', 'Languages': 'en_US en_CA'}
        )

    def test_source_uri_with_brackets_and_options(self):
        source = deb.DebLine(
            'deb [ arch=amd64 lang=en_US,en_CA ] '
            'http://example][.com/[release]/ubuntu suite main'
        )
        self.assertEqual(source.uris, ['http://example][.com/[release]/ubuntu'])
        self.assertDictEqual(
            source.options,
            {'Architectures': 'amd64', 'Languages': 'en_US en_CA'}
        )

    def test_source_uri_with_brackets_and_options_with_colons(self):
        source = deb.DebLine(
            'deb [ arch=amd64,arm:2 lang=en_US,en_CA ] '
            'http://example][.com/[release]/ubuntu suite main'
        )
        self.assertEqual(source.uris, ['http://example][.com/[release]/ubuntu'])
        self.assertDictEqual(
            source.options,
            {'Architectures': 'amd64 arm:2', 'Languages': 'en_US en_CA'}
        )

    def test_worst_case_sourcenario(self):
        source = deb.DebLine(
            'deb [ arch=amd64,arm:2,arm][ lang=en_US,en_CA ] '
            'http://example][.com/[release:good]/ubuntu suite main restricted '
            'nonfree not-a-component'
        )
        self.assertEqual(source.uris, ['http://example][.com/[release:good]/ubuntu'])
        self.assertEqual(source.suites, ['suite'])
        self.assertEqual(source.components, [
            'main', 'restricted', 'nonfree', 'not-a-component'
        ])
        self.assertDictEqual(
            source.options,
            {
                'Architectures': 'amd64 arm:2 arm][',
                'Languages': 'en_US en_CA'
            }
        )

    def test_source_code_source(self):
        source = deb.DebLine(
            'deb-src http://example.com/ suite main'
        )
        self.assertEqual(source.name, 'deb-example-com')
        self.assertEqual(source.types, [util.AptSourceType.SOURCE])

    def test_disabled_source(self):
        source = deb.DebLine(
            '# deb http://example.com/ suite main'
        )
        self.assertEqual(source.name, 'deb-example-com')
        # pylint: disable=no-member
        # This works fine, so I think pylint is just confused.
        self.assertFalse(source.enabled.get_bool())
        # pylint: enable=no-member

    def test_disabled_source_without_space(self):
        source = deb.DebLine(
            '#deb http://example.com/ suite main'
        )
        self.assertEqual(source.name, 'deb-example-com')
        # pylint: disable=no-member
        # This works fine, so I think pylint is just confused.
        self.assertFalse(source.enabled.get_bool())
        # pylint: enable=no-member

    def test_source_with_trailing_comment(self):
        source = deb.DebLine(
            'deb http://example.com/ suite main # This is a comment'
        )
        self.assertEqual(source.name, 'deb-example-com')
        self.assertEqual(source.suites, ['suite'])
        self.assertEqual(source.components, ['main'])

    def test_disabled_source_with_trailing_comment(self):
        source = deb.DebLine(
            '# deb http://example.com/ suite main # This is a comment'
        )
        self.assertEqual(source.name, 'deb-example-com')
        self.assertEqual(source.suites, ['suite'])
        # pylint: disable=no-member
        # This works fine, so I think pylint is just confused.
        self.assertFalse(source.enabled.get_bool())
        # pylint: enable=no-member
        self.assertEqual(source.components, ['main'])

    @unittest.expectedFailure
    def test_cdrom_source(self):
        source = deb.DebLine(
            '# deb cdrom:[This is a CD-ROM Source] suite main # This is a comment'
        )
        self.assertEqual(source.uris, ['cdrom:[This is a CD-ROM Source]'])
