#  repolib PPA Signing Key Support
#
#  From software-properties
#
#  Copyright (c) 2004-2009 Canonical Ltd.
#            (c) 2019 Ian Santopietro <isantop@gmail.com>
#
#  Author: Michael Vogt <mvo@debian.org>
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation; either version 2 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
#  USA

from __future__ import print_function

import apt_pkg
import json
import os
import subprocess
import time

from threading import Thread

import urllib.request
from urllib.error import HTTPError, URLError
import urllib.parse
from http.client import HTTPException


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

class PPAException(Exception):
    pass

def get_info_from_lp(owner_name, ppa):
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
            lp_page = urllib.request.urlopen(request,
                                             cafile=LAUNCHPAD_PPA_CERT)
            return lp_page.read().decode("utf-8", "strict")
        except (HTTPException, URLError) as e:
            err = PPAException(
                "Error reading %s (%d tries): %s" % (lp_url, trynum, e.reason),
                e)
            # do not retry on 404. HTTPError is a subclass of URLError.
            if isinstance(e, HTTPError) and e.code == 404:
                break
        try:
            time.sleep(next(sleep_waits))
        except StopIteration:
            break

    raise err

def add_key(ppa_line):
    raw_ppa = ppa_line.replace('ppa:','').split('/')
    ppa_owner = raw_ppa[0]
    ppa = raw_ppa[1]
    ppa_info = get_info_from_lp(ppa_owner, ppa)
    apt_key_cmd = "apt-key adv --keyserver keyserver.ubuntu.com --recv-keys".split()
    apt_key_cmd.append(ppa_info['signing_key_fingerprint'])
    get_key = subprocess.run(apt_key_cmd)