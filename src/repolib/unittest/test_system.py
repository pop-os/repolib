#!/usr/bin/python3

"""
Copyright 2026 System76
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
from pathlib import Path

from .. import system, util


class SystemTestCase(unittest.TestCase):
    def setUp(self):
        util.set_testing()
        self.test_sources = {
            "example-legacy.list": "deb https://foo.example.com stable main\n",
            "example-deb822.sources": (
                "Types: deb\n"
                "URIs: https://packages.example.com\n"
                "Suites: stable\n"
                "Components: main\n"
                "Architectures: amd64\n"
                "Signed-By: /usr/share/keyrings/example.gpg\n"
            ),
        }
        util.SOURCES_DIR.mkdir(parents=True)
        for name, content in self.test_sources.items():
            src_path = Path(util.SOURCES_DIR / name)
            with open(src_path, mode="w") as output_file:
                output_file.write(content)

    def test_load_all_sources(self):
        system.load_all_sources()
        self.assertEqual(len(util.sources), len(self.test_sources))
        self.assertTrue("example-legacy" in util.sources)
        self.assertTrue("example-deb822" in util.sources)
        self.assertTrue("example-legacy.list" in util.files)
        self.assertTrue("example-deb822.sources" in util.files)
