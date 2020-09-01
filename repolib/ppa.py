#! /usr/bin/python3

"""
repolib PPA Signing Key Support

From software-properties

Copyright (c) 2004-2009 Canonical Ltd.
          (c) 2019-2020 Ian Santopietro <isantop@gmail.com>

Author: Michael Vogt <mvo@debian.org>
        Ian Santopietro <isantop@gmail.com>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
USA
"""
#pylint: disable=too-many-ancestors
# If we want to use the subclass, we don't have a lot of options.

from __future__ import print_function

import json
import subprocess
import time
import urllib.parse
import urllib.request
from http.client import HTTPException
from urllib.error import HTTPError, URLError

from . import source, util

DISTRO_CODENAME = util.DISTRO_CODENAME

SKS_KEYSERVER = 'https://keyserver.ubuntu.com/pks/lookup?op=get&options=mr&exact=on&search=0x%s'
# maintained until 2015
LAUNCHPAD_PPA_API = 'https://launchpad.net/api/devel/%s/+archive/%s'
LAUNCHPAD_USER_API = 'https://launchpad.net/api/1.0/%s'
LAUNCHPAD_USER_PPAS_API = 'https://launchpad.net/api/1.0/%s/ppas'
LAUNCHPAD_DISTRIBUTION_API = 'https://launchpad.net/api/1.0/%s'
LAUNCHPAD_DISTRIBUTION_SERIES_API = 'https://launchpad.net/api/1.0/%s/%s'
# Specify to use the system default SSL store; change to a different path
# to test with custom certificates.
LAUNCHPAD_PPA_CERT = "/etc/ssl/certs/ca-certificates.crt"

class PPALine(source.Source):
    """ A source specifically for Launchpad PPAs

    These are typically given in the format ppa:owner/name. This is a
    convenience function which makes adding these sources easier. Most of this
    code was adopted from SoftwareProperties.

    Arguments:
        line (str): The ppa: format line.
        fetch_data (bool): Whether to try and fetch metadata from LP.
    """
    # pylint: disable=too-many-instance-attributes
    # These just have more data than a normal source, and most of these are
    # @properties anyway (due to the inheritance from source.Source).

    def __init__(self, line, fetch_data=True, verbose=False):
        super().__init__()
        self.ppa_line = line
        self.verbose = verbose
        if not self.ppa_line.startswith('ppa:'):
            raise util.RepoError("The PPA %s is malformed!" % self.ppa_line)

        self.load_from_ppa(fetch_data=fetch_data)

    def load_from_ppa(self, fetch_data=True):
        """ Load PPA information from the PPA.

        Arguments:
            fetch_data (bool): Whether to fetch metadata from Launchpad.
        """
        self.init_values()
        self.enabled = 'yes'

        raw_ppa = self.ppa_line.replace('ppa:', '').split('/')
        ppa_owner = raw_ppa[0]
        ppa_name = raw_ppa[1]

        ppa_info = self.ppa_line.split(":")
        ppa_uri = 'http://ppa.launchpad.net/{}/ubuntu'.format(ppa_info[1])
        self.set_source_enabled(False)
        self.uris = [ppa_uri]
        self.suites = [DISTRO_CODENAME]
        self.components = ['main']
        ppa_name = ppa_info[1].split('/')
        self.name = 'ppa-{}'.format('-'.join(ppa_name))
        self.filename = '{}.sources'.format(self.name)
        if fetch_data:
            self.ppa_info = get_info_from_lp(ppa_owner, ppa_name[1])
            if self.verbose:
                print(self.ppa_info)
            self.name = self.ppa_info['displayname']
        self.enabled = util.AptSourceEnabled.TRUE

    def make_name(self):
        """ Make a name suitable for a PPA.

        Returns:
            str: The name generated.
        """
        try:
            ref = self.ppa_info['reference'].replace('/', '-')
            name = f'{ref}-{self.suites[0]}.sources'
        except (TypeError, AttributeError):
            name = f'{self.ppa_line.split(":")[1]}'

        return name.replace("~", "")

    def save_to_disk(self, save=True):
        """
        Saves the PPA to disk, and fetches the signing key.
        """
        self._get_ppa_key()
        if save:
            super().save_to_disk()

    def copy(self, source_code=True):
        """ Copies the source and returns an identical source object.

        Arguments:
            source_code (bool): if True, output an identical source, except with
                source code enabled.

        Returns:
            A Source() object identical to self.
        """
        new_source = PPALine(self.ppa_line)
        new_source = self._copy(new_source, source_code=source_code)
        return new_source

    def _get_ppa_key(self):
        if self.ppa_line:
            add_key(self.ppa_info['signing_key_fingerprint'])

def get_info_from_lp(owner_name, ppa):
    """ Attempt to get information on a PPA from launchpad over the internet.

    Arguments:
        owner_name (str): The Launchpad user owning the PPA.
        ppa (str): The name of the PPA

    Returns:
        json: The PPA information as a JSON object.
    """
    if owner_name[0] != '~':
        owner_name = '~' + owner_name
    lp_url = LAUNCHPAD_PPA_API % (owner_name, ppa)
    data = _get_https_content_py3(lp_url, True)
    return json.loads(data)

def _get_https_content_py3(lp_url, accept_json, retry_delays=None):
    if retry_delays is None:
        retry_delays = []

    trynum = 0
    err = None
    sleep_waits = iter(retry_delays)
    headers = {"Accept": "application/json"} if accept_json else {}

    while True:
        trynum += 1
        try:
            request = urllib.request.Request(str(lp_url), headers=headers)
            lp_page = urllib.request.urlopen(request)
            return lp_page.read().decode("utf-8", "strict")
        except (HTTPException, URLError) as errr:
            err = util.RepoError(
                "Error reading %s (%d tries): %s" % (lp_url, trynum, errr.reason),
                errr)
            # do not retry on 404. HTTPError is a subclass of URLError

            # pylint: disable=no-member
            # Yes it does, and this works fine. Not sure why things complain.
            if isinstance(errr, HTTPError) and errr.code == 404:
                break
        try:
            time.sleep(next(sleep_waits))
        except StopIteration:
            break

    raise err

def add_key(fingerprint):
    """ Add a key for a PPA into the system configuration.

    Arguments:
        fingerprint (str): The fingerprint of the key to add.
    """
    apt_key_cmd = "apt-key adv --keyserver keyserver.ubuntu.com --recv-keys".split()
    # apt_key_cmd.append(ppa_info['signing_key_fingerprint'])
    apt_key_cmd.append(fingerprint)
    subprocess.run(
        apt_key_cmd,
        check=False
    )
