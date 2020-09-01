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
                '## X-Repolib-Name: deb-example-com\n'
                'deb [arch=armel,amd64 lang=en_US] http://example.com ubuntu main\n'
                'deb-src [arch=armel,amd64 lang=en_US] http://example.com ubuntu main\n'
            )
        self.source = legacy_deb.LegacyDebSource(filename='test.list')
        self.source.load_from_file()

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
        expected = '## Added/managed by repolib ##\n#\n## X-Repolib-Name: deb-example-com\ndeb [arch=amd64] https://example.com ubuntu main universe\ndeb-src [arch=amd64] https://example.com ubuntu main universe\n'
        actual = self.source.make_deblines()
        self.assertEqual(actual, expected)

    def test_validate(self):
        testline1 = '# deb http://example.com ubuntu main'
        testline2 = 'deb http://example.com ubuntu main'
        testline3 = '#deb-src http://example.com ubuntu main'
        testline4 = 'deb-src http://example.com ubuntu main'
        testline5 = '# dbe http://example.com ubuntu main'
        testline6 = 'dba http://example.com ubuntu main'

        for line in [testline1, testline2, testline3, testline4]:
            self.assertTrue(util.validate_debline(line))

        for line in [testline5, testline6]:
            self.assertFalse(util.validate_debline(line))

    def test_save_to_disk(self):
        with open(util.get_sources_dir(testing=True) / 'test2.list', mode='r') as expected_file:
            expected_data = expected_file.readlines()

        with open(util.get_sources_dir(testing=True) / 'test.list', mode='r') as source_file:
            source_data = source_file.readlines()
        self.assertNotEqual(source_data, expected_data)

        for source in self.source.sources:
            source.uris = ['http://example.com']
            source.options = {
                'Architectures': 'armel amd64',
                'Languages': 'en_US'
            }
            source.components = ['main']
        self.source.filename = 'test3.list'
        self.source.save_to_disk()

        with open(util.get_sources_dir(testing=True) / 'test3.list', mode='r') as source_file:
            source_file.seek(0)
            source_data = source_file.readlines()
        self.assertEqual(source_data, expected_data)
