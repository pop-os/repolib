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

from ..shortcuts import ppa
from .. import util

class PPATestCase(unittest.TestCase):
    
    def test_ppa(self):
        source = ppa.PPASource()
        
        # Verification data
        uris_test = ['http://ppa.launchpad.net/system76/pop/ubuntu']
        signed_test = '/usr/share/keyrings/ppa-system76-pop-archive-keyring.gpg'
        source.load_from_shortcut(shortcut='ppa:system76/pop', meta=False, key=False)

        self.assertEqual(source.uris, uris_test)
        self.assertEqual(source.ident, 'ppa-system76-pop')
        self.assertEqual(source.suites, [util.DISTRO_CODENAME])
        self.assertEqual(source.components, ['main'])
        self.assertEqual(source.types, [util.SourceType.BINARY])
