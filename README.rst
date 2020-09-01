=======
RepoLib
=======

RepoLib is a Python library and CLI tool-set for managing your software 
system software repositories. It's currently set up to handle APT repositories
on Debian-based linux distributions. 

RepoLib is intended to operate on DEB822-format sources. It aims to provide
feature parity with software-properties for most commonly used functions.

Documentation
=============

Documentation is available online at `Read The Docs <https://repolib.rtfd.io/>`_.


Basic CLI Usage
-----------

RepoLib includes a CLI program for managing software repositories, 
:code:`apt-manage`
.

Usage is divided into subcommands for most tasks. Currently implemented commands
are:

    apt-manage add # Adds repositories to the system

Additional information is available with the built-in help:

    apt-manage --help
    
Add
^^^

Apt-manage allows entering a URL for a repository, a complete debian line, or a
Launchpad PPA shortcut (e.g. "ppa:user/repo"). It also adds signing keys for PPA
style repositories automatically. 

Installation
============

From System Package Manager
---------------------------

If your operating system packages repolib, you can install it by running::
    
    sudo apt install python3-repolib


Uninstall
^^^^^^^^^

To uninstall, simply do::
    
    sudo apt remove python3-repolib


From PyPI
---------

Repolib is available on PyPI. You can install it for your current user with::

    pip3 install repolib

Alternatively, you can install it system-wide using::

    sudo pip3 install repolib

Uninstall
^^^^^^^^^

To uninstall, simply do::

    sudo pip3 uninstall repolib

From Git
--------

First, clone the git repository onto your local system::

    git clone https://github.com/isantop/repolib
    cd repolib

Debian
------

On debian based distributions, you can build a .deb package locally and install 
it onto your system. You will need the following build-dependencies:

    * debhelper (>=11)
    * dh-python
    * python3-all
    * python3-setuptools

You can use this command to install these all in one go::

    sudo apt install debhelper dh-python python3-all python3-setuptools

Then build and install the package::

    debuild -us -uc 
    cd ..
    sudo dpkg -i python3-repolib_*.deb

Uninstall
^^^^^^^^^

To uninstall, simply do::

    sudo apt remove python3-repolib

setuptools setup.py 
-------------------

You can build and install the package using python3-setuptools. First, install 
the dependencies::

    sudo apt install python3-all python3-setuptools

Then build and install the package::

    sudo python3 ./setup.py install

Uninstall
^^^^^^^^^

You can uninstall RepoLib by removing the following files/directories:

    * /usr/local/lib/python3.7/dist-packages/repolib/
    * /usr/local/lib/python3.7/dist-packages/repolib-\*.egg-info
    * /usr/local/bin/apt-manage

This command will remove all of these for you::

    sudo rm -r /usr/local/lib/python3.7/dist-packages/repolib* /usr/local/bin/apt-manage
