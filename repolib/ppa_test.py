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
        self.assertFalse(self.source.options)

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
