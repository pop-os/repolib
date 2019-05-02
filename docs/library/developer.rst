.. _repolib-module:

=======
RepoLib 
=======

The :ref:`repolib-module` module simplifies working with APT sources, especially 
those stored in the DEB822 format. It translates these sources into Python 
Objects for easy reading, parsing, and manipulation of them within Python 
programs. The program takes a user-defined sources filename and reads the 
contents, parsing it into a Python object which can then be iterated upon and 
which uses native data types where practicable. The :ref:`repolib-module` module 
also allows easy creation of new DEB822-style sources from user-supplied data.

Example
=======

The following code is a Python prgram that creates an ``example.sources`` file 
in `/etc/apt/sources.list.d/` with some sample data, and then modifies the 
suites used by the source and prints it to the console, before finally saving 
the new, modified source to disk::

    import repolib
    source = repolib.Source(
        filename='example.sources',
        name='Example Source', enabled=True, types=['deb', 'deb-src'],
        suites=['disco'], components=['main'], 
        options={'Architectures': ['amd64', 'armel']}
    )
    
    source.suites.append('cosmic')
    source.uris.append('http://example.com/ubuntu')
    
    print(source.make_source_string())
    
    source.save_to_disk()

When run with the appropriate arguments, it prints the contents of the source 
to disk and then saves a new ``example.sources`` file in ``/etc/apt/sources.list.d``::

    $ 
    Name: Example Source
    Enabled: yes
    Types: deb deb-src
    URIs: http://example.com/ubuntu
    Suites: disco cosmic
    Components: main
    Architectures: amd64 armel
    $ ls -la /etc/apt/sources.list.d/example.sources
    -rw-r--r-- 1 root root 159 May  1 15:21 /etc/apt/sources.list.d/example.sources

The following will walk you through this example.

Creating a Source Object
------------------------

The first step in using :ref:`repolib-module` is creating a :ref:`source-object`::

    source = repolib.Source(
        filename='example.sources',
        name='Example Source', enabled=True, types=['deb', 'deb-src'],
        suites=['disco'], components=['main'], 
        options={'Architectures': ['amd64', 'armel']}
    )

The :ref:'source-object' will hold all of the information about the 
source we're working with.

Adding and Manipulating Data
----------------------------

The :ref:`source-object` contains attributes which describe the various parts of 
the source that are required to fetch and install software. Generally, these 
attributes are lists of strings which describe the different parts of the source. 
These attributes can be set or retrieved like any other attributes::

    source.suites.append('cosmic')
    source.uris.append('http://example.com/ubuntu')

This will add a ``cosmic`` suite to our source (which already has a ``disco`` 
suite added), and add a URI from which to fetch software (which wasn't 
previously set during object instantiation. 

Saving Data to Disk
-------------------

Once a source has the correct data (either after modification or creation), we 
need to save it to disk in order for Apt to be made aware of it::

    source.save_to_disk()

When called, this writes the data contained within the :ref:`source-object` to
disk. This does not destroy the object, so that it may be further manipulated by 
the program.

.. note::
    While :ref:`source-object`s can be manipulated after using the 
    :ref:`save-to-disk-method`, any subsequent changes will not be automatically 
    written to the disk as well. You need to call the :ref:`save-to-disk-method` 
    again in order to save further changes.

.. _source-object:

Source object
=============

class repolib.Source (name='',enabled=True,types=[],uris=[],suites=[],components=[],options={},filename='example.source')
    Create a new :ref:`source-object`. All parameters should be passed as 
    keyword arguments. Each parameter has its own more detailed description 
    below, but in short they are:

        * :ref:`name` - The human-readable name of the source. (default: '')
        * :ref:`enabled` - Whether the source is enabled or not at creation. 
          (default: True)
        * :ref:`types` - A list of the types that the source should use.
          (default: [])
        * :ref:`uris` - A list of URIs from which to fetch software or check for 
          updates. (default: [])
        * :ref:`suites` - Suites in which to narrow available software. (default: 
          [])
        * :ref:`components` - Components of the source repository to enable. 
          (default: [])
        * :ref:`options` - Optional items affecting the source. (default: {})
        * :ref:`filename` - The filename to save the source to on disk. 
          (default: 'example.sources')

The following decribe how each of these are used. 

.. _name:

name
----

This is a human-readable and nicely-formatted name to help a user recognize
what this source is. Any unicode character is allowed in this field. If a 
source is opened which doesn't have a name field, the filename will be used.

:ref:`name` is a string value, set to ``''`` by default. If there is no name in 
a loaded source, it will be set to the same as the filename (minus the 
extension).

This field maps to the ``X-Repolib-Name:`` field in the .sources file, which 
is ignored by Apt and other standards-compliant sources parsers.

.. _enabled:

enabled
-------

This a boolean value representing whether the source is enabled or not. A 
disabled source is excluded from updates and new software installs, but it can 
be easily re-enabled at any time. It defaults to ``True``.

This field maps to the ``Enabled:`` field in the .sources file. This is optional 
per the DEB822 standard, however if set to anything other than ``no``, the 
source is considered enabled.

.. _types:

types
-----

A list of string values describing the type of the repository. Valid values are
either ``deb`` for binary software or ``deb-src`` for source code. The default 
value for this argument is ``[]``.

This field maps to the ``Types:`` field in the sources file. 

.. _uris:

uris
----

A list of string values describing the URIs from which to fetch package lists 
and software for updates and installs. The currently recognized URI types are:

file
    The file scheme allows an arbitrary directory in the file system to be 
    considered an archive. This is useful for NFS mounts and local mirrors or 
    archives.

cdrom
    The cdrom scheme allows APT to use a local CD-ROM drive with media swapping. 
    Use the apt-cdrom(8) program to create cdrom entries in the source list.

http
    The http scheme specifies an HTTP server for the archive. If an environment 
    variable http_proxy is set with the format http://server:port/, the proxy 
    server specified in http_proxy will be used. Users of authenticated HTTP/1.1 
    proxies may use a string of the format http://user:pass@server:port/. Note 
    that this is an insecure method of authentication.

ftp
    The ftp scheme specifies an FTP server for the archive. APT's FTP behavior 
    is highly configurable; for more information see the apt.conf(5) manual 
    page. Please note that an FTP proxy can be specified by using the ftp_proxy 
    environment variable. It is possible to specify an HTTP proxy (HTTP proxy 
    servers often understand FTP URLs) using this environment variable and only 
    this environment variable. Proxies using HTTP specified in the configuration 
    file will be ignored.

copy
    The copy scheme is identical to the file scheme except that packages are 
    copied into the cache directory instead of used directly at their location. 
    This is useful for people using removable media to copy files around with APT.

rsh, ssh
    The rsh/ssh method invokes RSH/SSH to connect to a remote host and access 
    the files as a given user. Prior configuration of rhosts or RSA keys is 
    recommended. The standard find and dd commands are used to perform the file 
    transfers from the remote host.
  
.. note::
    Although these are the currently-recognized official URI types, Apt can be 
    extended with additional URI schemes through extension packages. Thus it is 
    **not** recommended to parse URIs by type and instead rely on user input 
    being correct and to throw exceptions when that isn't the case.

.. _suites:

suites
------

This value is a list of strings describing the suites against which to check for 
software. This is typically used to differentiate versions for the same OS, e.g. 
``disco`` or ``cosmic`` for Ubuntu. 

This value maps to the ``Suites:`` field in the sources file. 

.. _components:

components
----------

This value is a list of strings describing the enabled distro components to 
download software from. Common values include ``main``, ``restricted``, 
``nonfree``, etc.

.. _options:

options
-------

This is a dictionary containing key value pairs of options to add to the source. 
Options often are used to restrict a source to certain CPU architectures or 
languages. Valid options include:

Architectures
    Multivalue option defining for which architectures information should be 
    downloaded. If this option isn't set the default is all architectures as 
    defined by the APT::Architectures config option.

Languages 
    Multivalue option defining for which languages information such as 
    translated package descriptions should be downloaded. If this option isn't 
    set the default is all languages as defined by the Acquire::Languages config 
    option.

Targets
    Multivalue option defining which download targets apt will try to acquire 
    from this source. If not specified, the default set is defined by the 
    Acquire::IndexTargets configuration scope (targets are specified by their 
    name in the Created-By field). Additionally, targets can be enabled or 
    disabled by using the Identifier field as an option with a boolean value 
    instead of using this multivalue option.

PDiffs
    A yes/no value which controls if APT should try to use PDiffs to update old 
    indexes instead of downloading the new indexes entirely. The value of this 
    option is ignored if the repository doesn't announce the availability of 
    PDiffs. Defaults to the value of the option with the same name for a 
    specific index file defined in the Acquire::IndexTargets scope, which itself 
    defaults to the value of configuration option Acquire::PDiffs which defaults 
    to yes.

By-Hash
    Can have the value yes, no or force and controls if APT should try to acquire 
    indexes via a URI constructed from a hashsum of the expected file instead of 
    using the well-known stable filename of the index. Using this can avoid 
    hashsum mismatches, but requires a supporting mirror. A yes or no value 
    activates/disables the use of this feature if this source indicates support 
    for it, while force will enable the feature regardless of what the source 
    indicates. Defaults to the value of the option of the same name for a specific 
    index file defined in the Acquire::IndexTargets scope, which itself defaults 
    to the value of configuration option Acquire::By-Hash which defaults to yes.

.. _filename:

filename
--------

This is a string value describing the filename to save the source to when using 
the :ref:`save-to-disk-method`. 