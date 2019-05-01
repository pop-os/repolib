==============
Add Subcommand
==============

The ``add`` subcommand is used to add new repositories to the software sources.
Given without parameters, it will prompt for input to fill in the fields 
required to add the repository one by one::

    $ sudo apt-manage add
    Enter the URIs of the repository: http://ppa.launchpad.net/system76/pop/ubuntu
    Enter the suites/distros of the repository (e.g. "disco"): disco
    Enter the componenets of the repository (e.g. "main"): main
    Enter a name for this repository: System76 Pop!_OS Repository

The source will then be saved into the system. Additionally, you can specify
a deb-line to configure into the system or a ``ppa:`` shortcut to add the 
new source directly::

    $ sudo apt-manage add deb http://apt.pop-os.org/ubuntu disco main
    $ sudo apt-manage add ppa:system76/pop

These correctly expand into full DEB822 sources. If an internet connection is 
available, ``apt-manage`` will additionally attempt to install the signing key 
for any ``ppa:`` shortcuts added.

.. note::
    Even though ``apt-manage`` will add one-line style sources to the system, 
    it will not save them in this format. This is simply a convenience 
    feature and is not indicative of the added source format.

.. note::
    Because the ``add`` subcommand modifies system configuration, the use of 
    ``sudo`` or a root user account is required.
    