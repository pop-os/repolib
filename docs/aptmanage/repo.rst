================
Managing Sources
================

The ``repo`` subcommand is used for getting information about a source, or for 
configuring it. With no options, ``repo`` will list repository information::

    $ apt-manage repo system
    Name: System Sources
    Enabled: yes
    Types: deb deb-src
    URIs:  http://apt.pop-os.org/ubuntu http://archive.ubuntu.com/ubuntu
    Suites: disco disco-security disco-updates disco-backports
    Components: main universe restricted multiverse

You can also use the ``-i/--info`` flag for this purpose::

    $ apt-manage repo --info ppa-system76-pop
    Name: Pop!_OS PPA
    Enabled: yes
    Types: deb
    URIs: http://ppa.launchpad.net/system76/pop/ubuntu
    Suites: disco
    Components: main

.. note::
    The following options modify the system configuration, and thus require you 
    to use sudo or a root user.


Disabling/Enabling Sources
--------------------------

Disabling a source is useful if you want to temporarily stop receiving software 
or updates from the source. You can also use it have testing or unstable sources 
that you want to temporarily enable from time to time.

::

    $ sudo apt-manage repo --disable ppa-system76-proposed

If you want to re-enable a disabled source, you can use ``--enable``. ::

    $ sudo apt-manage repo --enable ppa-system76-proposed


Removing Sources
----------------

You can remove sources that you want to stop using permanently. ::

    $ sudo apt-manage repo --remove ppa-system76-proposed
