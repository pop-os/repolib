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
