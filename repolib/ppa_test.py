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

from urllib.error import URLError

from . import ppa
from . import util

class PPATestCase(unittest.TestCase):
    def setUp(self):
        self.source = ppa.PPALine(
            'ppa:system76/pop',
            fetch_data=False
        )

    def test_uri(self):
        self.assertEqual(
            self.source.uris,
            ['http://ppa.launchpad.net/system76/pop/ubuntu']
        )

    def test_name(self):
        self.assertEqual(self.source.name, 'ppa-system76-pop')

    def test_suite(self):
        self.assertEqual(self.source.suites, [util.DISTRO_CODENAME])

    def test_components(self):
        self.assertEqual(self.source.components, ['main'])

    def test_type(self):
        self.assertEqual(self.source.types, [util.AptSourceType.BINARY])

    def test_options(self):
        self.assertIsNone(self.source.options)

    def test_internet_features(self):
        try:
            self.source.load_from_ppa()
            self.assertEqual(self.source.name, 'Pop!_OS PPA')
            self.assertNotEqual(self.source.ppa_info, {})
        except util.RepoError as err:
            # pylint: disable=no-else-raise, no-member
            # This is a valid time to else raise since we're catching
            # a different type of error.
            if isinstance(err.args[-1], URLError):
                if "Name or service not known" in str(err.args[-1].reason):
                    raise unittest.SkipTest(
                        'Can\'t test internet features without network.'
                    )
                elif "Connection refused" in str(err.args[-1].reason):
                    raise unittest.SkipTest(
                        'Couldn\'t fetch details from network.'
                    )
            else:
                raise err
