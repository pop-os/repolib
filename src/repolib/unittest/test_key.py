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

from ..key import SourceKey
from .. import util, system
from .. import set_testing

# System76 Signing PubKey, for test import
KEY_DATA = (
    '-----BEGIN PGP PUBLIC KEY BLOCK-----\n\nmQINBFlL+3MBEADdNM9Xy2t3EtKU1i3R1o'
    '1OCgJqLiDm8OZZq47InYID8oAPKRjd\n0UDVJTrvfsB4oJH97VRi2hGv2xmc19OaFE/NsQBZW/'
    '7/3ypLr8eyaNgvscsmG/WN\ncM1cbMZtwd1b0JOr3bNTzp6WKRI3jo9uRw7duM8FwPjKm76Lbo'
    'DQbAR+4Szm3O8x\n/om8Gs1MRPUkY2dVz5KzednFLHwy7qnUXR3WRB5K1L9EBZkFDDNqnyViUI'
    'rE4bTm\nBC9mTg/Xfw/QXUFYz3t/YTYduAU0o1q2yei+8tVAJKh7H9t3PrQ95l3RUUcaAvba\n'
    'A9zlCrI8fonpxu7eSpkqzT4uCkfxdLVwittl1DumKTEkSXDQ5txY21igbSZZQwBA\nZf9MnFhJ'
    'fPsEIq2YHRc1FBcQxiAIpnGizv7FgYY5FxmZQ7592dMQOZ00h+lDSQug\nNMxloHCogaXR038u'
    'IKGTQnQEVcT46FtTRkLMSvbigy+RVSchdu9MEBBPgD3vSv53\nNEobXsLiZ9hF6Hk7XI2WxP5j'
    '1zWTPmzxvf9NDOWz2Sw9Z+ilf252LXoxZQaMngp8\nXL32uvw7q+mjB6F1W/qpe3b32uu7eGNr'
    'DWJ5veE808hpXXj803TllmRUfMGUrtY9\nk7uUTQQWtrJ5uZ0QmsTk1oJHCPIUjjuiNtQfq28+'
    'bfg8FEJ/F1N1mB0IvwARAQAB\ntCxQb3AgT1MgKElTTyBTaWduaW5nIEtleSkgPGluZm9Ac3lz'
    'dGVtNzYuY29tPokC\nNwQTAQIAIgUCWUv7cwIbAwYLCQgHAwIGFQgCCQoLBBYCAwECHgECF4AA'
    'CgkQIE3Y\nrsM6ev8kXw/4p/8fOH8wM59ZoU0t1+fv3O8dYaDdTVTVIEno9snrsx5A5tbMu59r'
    '\nHoBaxGenv/PB0l8yANhRX+HVmU/l0Sj0lTlEkYzgH/IT2Ne60s1ETgI7DlgSuYyP\nH8wq61'
    '85+2DyE2+R/XcXGq0I++QUq1Y6rS+B4KIyYcgpJotcVNFaZiwuJZE31uLg\nkVMZrm1oObHear'
    '7P2JQTbgsENMZDJEhQBCGKVdnAfVdKUeUrd07syr0cDe3kwY9o\ncNc00bhIh23cLTJE2omok9'
    'yCsXoeFJlPMyZw8WvEa5oaYWzP4Yw7nF8/27JTzZ70\nDjK2D2xoTkr0cP87LtZulS6FC3lxLu'
    'Z6hSaxsqoBH8Dd1uyYVEzLDsIRMtSHsXk+\n3kLrr1p7/7/vjGShlYkbLtP4jWnlHc6vSxIzm/'
    'MQmQMCfjeo3QH7GGw88mYtXngQ\n/Zna6wz0oL6pGM/4t90SCxTxRqCnoxMxzkcpt9n42bj79g'
    'rESOMH4wm3ExfuPk7I\nDtY+SqzIq0QvoPbC3XJLusWVgwUsRF2FpTTRTHEiWEMjWDKDVEyT4K'
    '1k1k3f/gi2\n6LdtXwqDwzUvJJU5HYwVFywt+0jt5F0ZlTlPizz3iHw4gMLOielRShl+gZrU2U'
    '0O\naj1Hyts9LymEKMUvRQGwMqCZcXo6sGjs59tTsfeGX16PTOyBri8eoLkCDQRZS/tz\nARAA'
    'pD9IWm4zS1AuBcOTuvh1E/ciKHGIUtW3JftD9ah8loEeckakgG5Xn9he1X6J\nyxPULpsptcCC'
    'cKXlw853ZQK9PLQJX6moWLH+qf2Zo3UAn/YEsWk+KsHoxPXHNUds\nu/j6UKkqEk8c7H92hUo8'
    'aWghO3p4HDVJ9KmGtueQ3jOv8Qun7Eh9cIo0A59cKmMv\njKUiYHLIJw8bkveQ8rVPul1ZHn56'
    'ORiBi58vm3tzjI4UWHQMjiKxXT6H5eG/f5K6\nuaK8lljh6n6jhdnQCpBcdtSIbhE/6YRv2+Ig'
    'L+BRssvprBtx4/sBwKjNNqzWPeGy\nUDHMiF88ETYqZ8DfukQ/e5XuaxjU41g/F8cw8BeVTBMv'
    'eb1YTyOoWcWvTL+hoBfS\nqYc/lvDHmmJ7/IgeMvUE6KoByP4ub5wX52mJTqgMC4GMhA04BC60'
    'B+NfVAXLh2pa\nTRJAHoWTDswOxbR6q9zPEFGZzV04B9Y96EavwMpT5IzG2fOPBwvdT0EDnt+v'
    'Q/iB\nc9O7CvkRTROAV+RoNCLY2XU8yNc/XxuI66PCE4Q96jW4uDzHvi6sPW/glsfRi2NT\nRW'
    'CO15KMVf0aypXeBpSbHIXIYGdXRQRpw980IW6PrElPpqZ5/DGbkXei5CuruF2R\nmltuu3MqYQ'
    'jcUvP9T7s0e5GAFgQFrR/8q29nVULq8IF4vzUAEQEAAYkCHwQYAQIA\nCQUCWUv7cwIbDAAKCR'
    'AgTdiuwzp6/wTGD/9Co4gEmTTOW++FneMMJo5K4WqeWVRg\ng1q5+yoVqgWq3k6lLsEC5kxR30'
    '5BAAcvXo9XPKdo62ySYmhIFOpIz/TkeTUxDZaw\nsLtcBxXUME2L5j/1od1V9lxecUvLAgA11o'
    '5Kb8TMKn5ZcmGhadtTLslWQcYsKqhw\nLaYQRlcxLDHYT8DXFkHgDhUMMbpt07dU5v5lIjgtGN'
    'HRhdS7/lCmSWOBtYapwpAH\nGYSmahN0zO36VHzOB5uwFue0tSoQiBEvLrCV/8ZtT2S5NkXaSm'
    'isz6B5Vr6DRtWI\nOamW5pMbSL8WQNQ99Kik05ctERjv2NgxI4JQo/a4KKthRrT4JlixXmrfJD'
    'uPyDPp\nRuTu1Elo6snoqWKQNf1sEPKvcv7EviNxBOhbTKivWrJXMnbOme7+UlNLcq7VAFp3\n'
    'x5hxk/ap0WqH/hs7+8jMBC8nS402MoM7EyLS0++kbOuEL/Prf3+JxFRqIu5Df77J\n+bUmTtKI'
    'CV43ikiVWmnP5OuJj2JPSOTR+rLxAQYpyHmo7HKXE63FbH1FVLgsT88+\nEW6VtI01I7EYmKQX'
    'EqQo52yfeHKDrQjGNVBWMKcXj0SVU+QQ1Ue/4yLwA+74VD2d\nfOyJI22NfTI+3SMAsMQ8L+WV'
    'QI+58bu7+iEqoEfHCXikE8BtTbJAN4Oob1lrjfOe\n5utH/lMP9suRWw==\n=NL3f\n-----EN'
    'D PGP PUBLIC KEY BLOCK-----\n'
)

class KeyTestCase(unittest.TestCase):
    def setUp(self):
        set_testing()
        self.key_data = KEY_DATA
        self.keys_dir = util.KEYS_DIR
        self.key_id = '204DD8AEC33A7AFF'
        self.key_uids = ['Pop OS (ISO Signing Key) <info@system76.com>']
        self.key_length = '4096'
        self.key_date = '1498151795'

    def test_import_ascii(self):
        key = SourceKey(name='popdev')
        key.load_key_data(ascii=self.key_data)
        key_dict = key.gpg.list_keys()[0]
        key_path = self.keys_dir / 'popdev-archive-keyring.gpg'

        self.assertEqual(key.path, key_path)
        self.assertEqual(len(key.gpg.list_keys()), 1)
        self.assertEqual(key_dict['keyid'], self.key_id)
        self.assertEqual(key_dict['uids'], self.key_uids)
        self.assertEqual(key_dict['length'], self.key_length)
        self.assertEqual(key_dict['date'], self.key_date)
    
    def test_key_save_load(self):
        print(self.keys_dir)
        key_path = self.keys_dir / 'popdev-archive-keyring.gpg'
        if key_path.exists():
            key_path.unlink()

        self.assertFalse(key_path.exists())
        key_save = SourceKey(name='popdev')
        key_save.load_key_data(ascii=self.key_data)
        key_save.save_gpg()

        self.assertTrue(key_save.path.exists())

        key_load = SourceKey()
        key_load.reset_path(name='popdev')
        key_dict = key_load.gpg.list_keys()[0]

        self.assertEqual(key_load.path, key_path)
        self.assertEqual(len(key_load.gpg.list_keys()), 1)
        self.assertEqual(key_dict['keyid'], self.key_id)
        self.assertEqual(key_dict['uids'], self.key_uids)
        self.assertEqual(key_dict['length'], self.key_length)
        self.assertEqual(key_dict['date'], self.key_date)
    
    def test_delete_key(self):
        key_path = self.keys_dir / 'popdev-archive-keyring.gpg'
        if key_path.exists():
            key_path.unlink()
        
        self.assertFalse(key_path.exists())

        self.assertFalse(key_path.exists())
        key_save = SourceKey(name='popdev')
        key_save.load_key_data(ascii=self.key_data)
        
        key_save.save_gpg()

        self.assertTrue(key_save.path.exists())

        key_load = SourceKey()
        key_load.reset_path(name='popdev')
        key_load.delete_key()

        self.assertFalse(key_load.path.exists())
