=================
Modifying Sources
=================

Modifications can be made to various configured sources using the ``modify`` 
subcommand. 

Enabling/Disabling Sources: --enable | --disable
================================================

Sources can be disabled, which prevents software/updates from being installed
from the source but keeps it present in the system configuration for later use 
or records for later. To disable a source, use ``--disable``::

    $ apt-manage modify ppa-system76-pop --disable

To re-enable a source after it's been disabled, use ``--enable``::

    $ apt-manage modify ppa-system76-pop --enable


Changing names of sources: --name
=================================

RepoLib allows setting up human-readable names for use in GUIs or other 
user-facing contexts. To set or change a name of a source, use ``--name``::

    $ apt-manage modify ppa-system76-pop --name "Pop_OS PPA"


Suites: --add-suite | --remove-suite
====================================

Suites for sources can be added or removed from the configuration. In one-line 
sources, these are added with multiple lines, since each one-line source can 
have only one suite each. DEB822 sources can have multiple suites.

To add a suite, use ``--add-suite``::

    $ apt-manage modify ppa-system76-pop --add-suite groovy

Use ``--remove-suite`` to remove a suite::

    $ apt-manage modify ppa-system76-pop --remove-suite focal


Components: --add-component | --remove-component
================================================

Both types of source format can have multiple components for each source. Note 
that all components for one-line format sources will share all of a source's 
components.

Components are managed similarly to suites::

    $ apt-manage modify system --add-component universe
    $ apt-manage modify system --remove-component restricted


URIs: --add-uri | --remove-uri
==============================

DEB822 sources may contain an arbitrary number of URIs. One-line sources require 
an additional line for each individual URI added. All suites on a source are all 
applied to all of the URIs equally.

URIs are managed similarly to both suites and components::

    $ apt-manage modify system --add-uri http://apt.pop-os.org/ubuntu
    $ apt-manage modify system --remove-uri http://us.archive.ubuntu.com/ubuntu


Notes
^^^^^

Multiple modifications may be applied on a single ``apt-manage modify`` calls::

    $ apt-manage modify system --name "Pop_OS 20.10 System Sources" \
        --add-suite groovy \
        --remove-suite focal focal-proposed \
        --add-uri http://apt.pop-os.org/ubuntu \
        --remove-uri http://us.archive.ubuntu.com/ubuntu
