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
#pylint: disable=too-many-ancestors
# If we want to use the subclass, we don't have a lot of options.

from . import source
from . import util

class SystemSourceException(Exception):
    """ System Source Exceptions. """

    def __init__(self, *args, code=1, **kwargs):
        """Exception with the system sources

        Arguments:
            msg (str): Human-readable message describing the error that threw the
                exception.
            code (:obj:`int`, optional, default=1): Exception error code.
    """
        super().__init__(*args, **kwargs)
        self.code = code

class SystemSource(source.Source):
    """ System Sources. """

    def __init__(self, filename='system.sources'):
        """ Constructor for System Sources

        Loads a source object for the System Sources. These are located (by
        default) in /etc/apt/sources.list.d/system.sources. If your distro uses
        a different location, please patch this in your packaging.
        """
        super().__init__()
        self.load_from_file(filename=filename)

    def set_component_enabled(self, component='main', enabled=True):
        """ Enables or disabled a repo component (e.g. 'main')

        Keyword Arguments:
            component -- The component to (en|dis)able (default: "main")
            ennabled -- Whether COMPONENT is enabled (default: True)
        """
        components = self.components.copy()
        if not enabled:
            if component in components:
                components.remove(component)
                self.components = components.copy()
                self.save_to_disk()
                return component
        else:
            if component not in components:
                self.enabled = True
                components.append(component)
                self.components = components.copy()
                self.save_to_disk()
                return component

        raise SystemSourceException(
            msg=f"Couldn't toggle component: {component} to {enabled}"
        )

    def set_suite_enabled(self, suite=util.DISTRO_CODENAME, enabled=True):

        """ Enables or disabled a repo suite (e.g. 'main')

        Keyword Arguments:
            suite -- The suite to (en|dis)able (default: main)
            ennabled -- Whether COMPONENT is enabled (default: True)
        """
        suites = self.suites.copy()
        if not enabled:
            if suite in suites:
                suites.remove(suite)
                self.suites = suites.copy()
                self.save_to_disk()
                return suite
        else:
            if suite not in suites:
                self.enabled = True
                suites.append(suite)
                self.suites = suites.copy()
                self.save_to_disk()
                return suite


        raise SystemSourceException(
            msg=f"Couldn't toggle suite: {suite} to {enabled}"
        )
