==============
Adding Sources
==============

The ``add`` subcommand is used to add new repositories to the software sources.
You can specify a deb-line to configure into the system or a ``ppa:`` shortcut 
to add the new source directly::

    $ sudo apt-manage add deb http://apt.pop-os.org/ubuntu disco main
    $ sudo apt-manage add ppa:system76/pop

If an internet connection is available, ``apt-manage`` will additionally attempt 
to install the signing key for any ``ppa:`` shortcuts added.


Options for adding sources
==========================

Various options control adding sources to the system.


Source Code, Details, Disabling Sources
---------------------------------------

To enable source code for the added repository, use the ``--source-code`` flag::

    $ apt-manage add --source-code ppa:system76/pop

The new source can be disabled upon adding it using the ``--disable`` flag::

    $ apt-manage add --disable ppa:system76/pop

Details for the PPA can be printed for review prior to adding the source using 
the ``--expand`` flag::

    $ apt-manage add --expand ppa:system76/pop
    Name: Pop!_OS PPA
    Enabled: yes
    Types: deb
    URIs: http://ppa.launchpad.net/system76/pop/ubuntu
    Suites: focal
    Components: main

    A repository for all Pop!_OS software components.

    Press [ENTER] to contine or Ctrl + C to cancel.

This will print the generated configuration for the source as well as any 
available details fetched for the source (typically only available for PPA 
sources).


Names and Identifiers
---------------------

Names for PPA sources are automatically detected from Launchpad if an internet
connection is available. Otherwise they are automatically generated based on the 
source type and details. Optionally, a name can be specified when the source is 
added::

    $ apt-manage add ppa:system76/pop --name "PPA for Pop_OS Software"

System-identifiers determine how the source is subsequently located within RepoLib and 
on the system. It matches the filename for the source's configuration file. It 
is automatically generated based on the source type, or can be specified 
manually upon creation using the ``--identifier`` flag::

    $ apt-manage add ppa:system76/pop --identifier pop-ppa

.. note::
    Even though ``apt-manage`` allows modifcation or management of DEB822-format
    sources, it does not currently support adding them to the system directly. 
    DEB822 sources can be manually added or added using third-party tools, and 
    ``apt-manage`` will correctly operate on them subsequently.
