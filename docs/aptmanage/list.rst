=============================
Listing Configuration Details
=============================

To get a list of all of the sources configured on the system, use the ``list``
subcommand::

    $ apt-manage list
    Configured sources:
    system - Pop_OS System Sources
    pop-os-apps - Pop_OS Applications
    ppa-system76-pop - Pop!_OS PPA

The sources are listed with the system source (if detected/configured) first, 
followed by all DEB822-format sources detected first, then by all one-line 
format sources. The system-identifier (used to identify sources in the system) 
is listed at the beginning of the line, and the name of the source is listed 
after.

Details of an individual source can be printed by specifying a source's 
system-identifier::

    $ apt-manage list ppa-system76-pop
    Details for source ppa-system76-pop:
    Name: Pop!_OS PPA
    Enabled: yes
    Types: deb deb-src
    URIs: http://apt.pop-os.org/release
    Suites: focal
    Components: main


Listing all details of all sources at once
==========================================

Details about all sources can be listed at once using the ``--verbose`` flag::

    $ apt-manage list --verbose
    Configured sources:
    system - Pop_OS System Sources
    Name: Pop_OS System Sources
    Enabled: yes
    Types: deb deb-src
    URIs: http://us.archive.ubuntu.com/ubuntu/
    Suites: focal focal-security focal-updates focal-backports
    Components: main restricted universe multiverse

    pop-os-apps - Pop_OS Applications
    Name: Pop_OS Applications
    Enabled: yes
    Types: deb
    URIs: http://apt.pop-os.org/proprietary
    Suites: focal
    Components: main

    ppa-system76-pop - Pop!_OS PPA
    Name: Pop!_OS PPA
    Enabled: yes
    Types: deb deb-src
    URIs: http://apt.pop-os.org/release
    Suites: focal
    Components: main

Note
^^^^

Passing the ``--verbose`` flag only applies to listing all sources. It has no 
effect if a source is specified using the system-identifier; in that case, only 
the specified source is printed. Additionally, if there are sources files which 
contain errors, the ``--verbose`` flag will print details about them, including 
the contents of the files and the stack trace of the exception which caused the 
error.


Legacy sources.list entries
===========================

The contents of the system ``sources.list`` file can be appended to the end of 
the output using the ``--legacy`` flag.