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

.. toctree::
    :maxdepth: 1
    :caption: RepoLib

    source/source
    ppa-module
    util-module
    enums

==================
``repolib`` Module
==================

The ``repolib`` Module is the main module for the package. It allows interfacing 
with the various Classes, Subclasses, and Functions provided by RepoLib. 

Module-level Attributes
=======================

There are a couple of module-level attributes and functions provided directly in 
the module.

.. _module-version

``VERSION``
-----------

repolib.VERSION
    Provides the current version of the library.

.. _module-get-all-sources

get_all_sources()
-----------------

repolib.get_all_sources(get_system=False)
    Returns a ``list`` of all configured sources currently on the system. If 
    ```get_system`` (default: ``False``) is ``True``, then the system source (if 
    configured and detected) will be included as the first item in the list.


Example
=======

The following code is a Python prgram that creates an ``example.sources`` file 
in `/etc/apt/sources.list.d/` with some sample data, and then modifies the 
suites used by the source and prints it to the console, before finally saving 
the new, modified source to disk::

    import repolib
    source = repolib.Source(ident='example')
    
    source.name = 'Example Source'
    source.types = ['deb', 'deb-src']
    source.uris = ['http://example.com/ubuntu']
    source.suites = ['focal']
    source.components = ['main']
    
    print(source.make_source_string())
    
    source.save_to_disk()

When run with the appropriate arguments, it prints the contents of the source 
to console and then saves a new ``example.sources`` file in 
``/etc/apt/sources.list.d``::

    $ 
    Name: Example Source
    Enabled: yes
    Types: deb deb-src
    URIs: http://example.com/ubuntu
    Suites: focal
    Components: main
    $ ls -la /etc/apt/sources.list.d/example.sources
    -rw-r--r-- 1 root root 159 May  1 15:21 /etc/apt/sources.list.d/example.sources

The following will walk you through this example.

Creating a Source Object
------------------------

The first step in using :ref:`repolib-module` is creating a :ref:`source-object`::

    source = repolib.Source(ident='example')

The :ref:'source-object' will hold all of the information about the 
source we're working with.

Adding and Manipulating Data
----------------------------

The :ref:`source-object` contains attributes which describe the various parts of 
the source that are required to fetch and install software. Generally, these 
attributes are lists of strings which describe the different parts of the source. 
These attributes can be set or retrieved like any other attributes::

    source.suites = ['focal']
    source.uris. = ['http://example.com/ubuntu']

This will add a ``focal`` suite to our source and add a URI from which to fetch 
software. 

:ref:`source-object` also presents a dict-like interface for setting and getting 
data, due to the inherited deb822 class. Key values are case insensitive and 
their order within the object are preserved. The Keys map to the corresponding 
attributes as follows:

    X-Repolib-Name: name
    Enabled: enabled
    Types: types
    URIs: uris
    Suites: suites
    Components: components

Option keys will mapt to the ``options`` attribute(``dict``).

Saving Data to Disk
-------------------

Once a source has the correct data (either after modification or creation), we 
need to save it to disk in order for Apt to be made aware of it::

    source.save_to_disk()

When called, this writes the data contained within the :ref:`source-object` to
disk. This does not destroy the object, so that it may be further manipulated by 
the program.

.. note::
    While :ref:`source-object` data can be manipulated after using the 
    :ref:`save-to-disk` method, any subsequent changes will not be automatically 
    written to the disk as well. You need to call :ref:`save-to-disk` again in
    order to save further changes.

.. _source-object:
