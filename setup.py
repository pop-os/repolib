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
#pylint: disable=invalid-name,subprocess-run-check
# We don't need to check these in setup

import os
import subprocess
from setuptools import setup, find_packages, Command

def get_version():
    """ Get the program version. """
    #pylint: disable=exec-used
    # Just getting the version.
    version = {}
    with open(os.path.join('repolib', '__version__.py')) as fp:
        exec(fp.read(), version)
    return version['__version__']

with open("README.rst", "r") as fh:
    long_description = fh.read()

classifiers = [
    'Environment :: Console',
    'Intended Audience :: System Administrators',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    'Natural Language :: English',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: System'
]

class Release(Command):
    """ Generate a release and push it to git."""
    description = "Generate a release and push it to git."

    user_options = [
        ('dry-run', None, 'Skip the actual release and do a dry run instead.'),
        ('skip-deb', None, 'Skip doing a debian update for this release.'),
        ('skip-git', None, 'Skip committing to git at the end.'),
        ('prerelease=', None, 'Release a pre-release version (alpha,beta,rc)'),
        ('increment=', None, 'Manually specify the desired increment (MAJOR, MINOR, PATCH)')
    ]

    def initialize_options(self):
        self.dry_run = False
        self.skip_deb = False
        self.skip_git = False
        self.prerelease = None
        self.increment = None

    def finalize_options(self):
        pass

    def run(self):
        cz_command = ['cz', 'bump', '--yes']
        ch_command = ['dch']
        git_command = ['git', 'add', '.']

        def capture_version(sp_complete):
            output = sp_complete.stdout.decode('UTF-8').split('\n')
            print('\n'.join(output))
            for line in output:
                if 'tag to create' in line:
                    version_line = line

            try:
                return version_line.split()[-1].replace('v', '')
            except UnboundLocalError:
                stderr = sp_complete.stderr.decode('UTF-8')
                print("WARNING: Couldn't get updated version! Using current.")
                print(stderr)
                return get_version()

        if self.dry_run:
            print('Dry run: Not making actual changes')
            cz_command.append('--dry-run')

        if self.prerelease:
            if self.prerelease.lower() not in ['alpha', 'beta', 'rc']:
                raise Exception(
                    f'{self.prerelease} is not a valid prerelease type. Please '
                    'use one of "alpha", "beta", or "rc".'
                )
            cz_command.append('--prerelease')
            cz_command.append(self.prerelease.lower())

        if self.increment:
            if self.increment.upper() not in ['MAJOR', 'MINOR', 'PATCH']:
                raise Exception(
                    f'{self.increment} is not a valid increments. Please use '
                    'one of MAJOR, MINOR, or PATCH.'
                )
            cz_command.append('--increment')
            cz_command.append(self.increment.upper())

        # We need to get the new version from CZ, as the file hasn't been
        # updated yet.
        version_command = cz_command.copy()
        version_command.append('--dry-run')
        version_complete = subprocess.run(version_command, capture_output=True)

        version = capture_version(version_complete)
        print(f'Old Version: {get_version()}')
        print(f'New version: {version}')

        ch_command.append(f'-v{version}')
        if not self.skip_deb:
            print(ch_command)
            if not self.dry_run:
                subprocess.run(ch_command)
                subprocess.run(['dch', '-r', '""'])

        if not self.skip_git:
            print(git_command)
            if not self.dry_run:
                subprocess.run(git_command)

        print(' '.join(cz_command))
        if not self.dry_run:
            subprocess.run(cz_command)

class Test(Command):
    """ Run pyflakes and pytest"""
    description = 'Run pyflakes, pytest, and pylint'

    user_options = [
        ('run-flakes', None, 'Run pyflakes'),
        ('skip-test', None, 'Skip running pytest'),
        ('skip-lint', None, 'Skip running pylint')
    ]

    def initialize_options(self):
        self.run_flakes = True
        self.skip_test = False
        self.skip_lint = False

    def finalize_options(self):
        pass

    def run(self):
        pytest_command = ['pytest-3']
        flakes_command = ['pyflakes3', 'repolib']
        lint_command = ['pylint', 'repolib']

        if not self.skip_test:
            subprocess.run(pytest_command)

        if not self.run_flakes:
            subprocess.run(flakes_command)

        if not self.skip_lint:
            subprocess.run(lint_command)

setup(
    name='repolib',
    version=get_version(),
    author='Ian Santopietro',
    author_email='ian@system76.com',
    url='https://github.com/pop-os/repolib',
    description='Easily manage software sources',
    download_url='https://github.com/pop-os/repolib/releases',
    long_description=long_description,
    tests_require=['pytest'],
    license='LGPLv3',
    packages=['repolib', 'repolib/command'],
    cmdclass={'release': Release, 'test': Test},
    scripts=['bin/apt-manage'],
    data_files=[
        ('share/bash-completion/completions', ['data/bash-completion/apt-manage']),
        ('share/zsh/vendor-completions', ['data/zsh-completion/_apt-manage']),
        ('/usr/share/dbus-1/system-services', ['data/org.pop_os.repolib.service']),
        ('/usr/share/polkit-1/actions', ['data/org.pop_os.repolib.policy']),
        ('/etc/dbus-1/system.d/', ['data/org.pop_os.repolib.conf']),
        ('/usr/lib/repolib', ['data/service.py', 'bin/add-apt-repository'])
    ]
)
