.. RepoLib documentation master file, created by
   sphinx-quickstart on Wed May  1 13:49:01 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

===================================
Welcome to RepoLib's documentation!
===================================

RepoLib is a Python library and CLI tool-set for managing your software 
system software repositories. It's currently set up to handle APT repositories
on Debian-based linux distributions. 

RepoLib is intended to operate on DEB822-format sources as well as legacy 
one-line format sources. It aims to provide feature parity with 
software-properties for most commonly used functions. It  also allows for 
simple, automated conversion from legacy "one-line" style  source to newer 
DEB822 format sources. These sources will eventually  deprecate the older 
one-line sources and are much easier to parse for both  human and machine. For a 
detailed explanation of the DEB822 Source format, see :ref:`deb822-explanation`.

RepoLib provides much faster access to a subset of ``SoftwareProperties`` 
features than ``SoftwareProperties`` itself does. Its scope is somewhat more 
limited because of this, but the performance improvements gained are substantial.
``SoftwareProperties`` also does not yet feature support for  managing DEB822 
format sources, and instead only manages one-line sources. 

RepoLib is available under the GNU LGPL.

.. contents:: Table of Contents
   :local:

.. toctree::
    :maxdepth: 4
    :caption: Developer Documentation

    library/developer

.. toctree::
    :maxdepth: 1
    :caption: RepoLib Documentation

    deb822-format

.. toctree:: 
    :maxdepth: 1
    :caption: apt-manage Documentation

    aptmanage/aptmanage

============
Installation
============

There are a variety of ways to install RepoLib

From System Package Manager
^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your operating system packages repolib, you can install it by running::
    
    sudo apt install python3-repolib


Uninstall
"""""""""

To uninstall, simply do::
    
    sudo apt remove python3-repolib


From PyPI
^^^^^^^^^

Repolib is available on PyPI. You can install it for your current user with::

    pip3 install repolib

Alternatively, you can install it system-wide using::

    sudo pip3 install repolib

Uninstall
"""""""""

To uninstall, simply do::

    sudo pip3 uninstall repolib

From Git
^^^^^^^^

First, clone the git repository onto your local system::

    git clone https://github.com/isantop/repolib
    cd repolib

Debian
^^^^^^

On debian based distributions, you can build a .deb package locally and install 
it onto your system. You will need the following build-dependencies:

    * debhelper (>= 11)
    * dh-python
    * lsb-release
    * python3-all
    * python3-dbus
    * python3-debian
    * python3-setuptools
    * python3-distutils
    * python3-pytest
    * python3-gnupg

You can use this command to install these all in one go::

    sudo apt install debhelper dh-python python3-all python3-setuptools python3-gnupg

Then build and install the package::

    debuild -us -uc 
    cd ..
    sudo dpkg -i python3-repolib_*.deb

Uninstall
"""""""""

To uninstall, simply do::

    sudo apt remove python3-repolib

setuptools setup.py 
^^^^^^^^^^^^^^^^^^^

You can build and install the package using python3-setuptools. First, install 
the dependencies::

    sudo apt install python3-all python3-setuptools

Then build and install the package::

    sudo python3 ./setup.py install

Uninstall
"""""""""

You can uninstall RepoLib by removing the following files/directories:

    * /usr/local/lib/python3.7/dist-packages/repolib/
    * /usr/local/lib/python3.7/dist-packages/repolib-\*.egg-info
    * /usr/local/bin/apt-manage

This command will remove all of these for you::

    sudo rm -r /usr/local/lib/python3.7/dist-packages/repolib* /usr/local/bin/apt-manage


|
|
|
|
|

Copyright © 2019-2022, Ian Santopietro
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

