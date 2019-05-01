#!/usr/bin/python3

"""
Copyright (c) 2019, Ian Santopietro
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

import subprocess

from setuptools import setup
from distutils.cmd import Command

version = {}
with open("repolib/__version__.py") as fp:
    exec(fp.read(), version)

with open("README.md", "r") as fh:
    long_description = fh.read()

classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: System Administrators',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Natural Language :: English',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: System'
]

def do_deb_release(vers):
    subprocess.run(['dch', '-v', vers])
    subprocess.run(['dch', '-r','""'])

class DebRelease(Command):
    """Basic sanity checks on our code."""
    description = 'Release a version to the debian packaging.'

    user_options = [
        ('version', None, 'Override the version to use'),
    ]

    def initialize_options(self):
        self.version = version['VERSION']

    def finalize_options(self):
        pass

    def run(self):
        do_deb_release(self.version)

setup(
    name = 'repolib',
    version = version['VERSION'],
    author = 'Ian Santopietro',
    author_email = 'isantop@gmail.com',
    url = 'https://github.com/isantop/repolib',
    description = 'Easily manage software sources',
    download_url = 'https://github.com/isantop/repolib/releases',
    long_description = long_description,
    license = 'BSD-2',
    packages=['repolib'],
    cmdclass={'release': DebRelease},
    scripts=['bin/apt-manage'],
    data_files=[
        ('/usr/share/bash-completion/completions', ['data/apt-manage']),
    ]
)