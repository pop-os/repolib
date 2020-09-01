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

from . import source
from . import util

class SourceTestCase(unittest.TestCase):
    def setUp(self):
        self.source = source.Source(filename='test.source')
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
        self.assertEqual(self.source.filename, 'test.source')

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
