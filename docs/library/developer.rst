.. _repolib_module:

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

.. _module_log_file_path

``LOG_FILE_PATH``
-----------------

repolib.LOG_FILE_PATH
    Stores the current path to the log file

.. _module_log_level

repolib.LOG_LEVEL
    Stores the current logging level. Note: Change this level using the 
    :ref:`module_set_logging_level` function.

.. _module_dirs

Configuration directories
=========================

repolib.KEYS_DIR
repolib.SOURCES_DIR
    Stores the current :obj:`Pathlib.Path` pointing at the signing key and 
    sources directories, respectively. Used for building path names and reading
    configuration.

.. _module_distro_codename:

DISTRO_CODENAME
===============

repolib.DISTRO_CODENAME
    The current CODENAME field from LSB. If LSB is not available, it will 
    default to ``linux``.


.. _module_clean_chars

CLEAN_CHARS
===========

repolib.CLEAN_CHARS 
    A ``dict`` which maps invalid characters for the :ref:`ident` attributes 
    which cannot be used and their replacements. These limitations are based on 
    invalid characters in unix-compatible filenames.

.. _module_sources

sources
=======

repolib.sources
    A :obj:`dict` storing all current sources configured on the system. To save
    resources, this list is only loaded/parsed when 
    :ref:`module_load_all_sources` is called, since many simple operations don't
    need the full list of currently-configured sources.

.. _module_files

files
=====

repolib.files
    A :obj:`dict` containing any source file objects present in the configured 
    sources dir (See :ref:`module_dirs`). This list is empty until 
    :ref:`module_load_all_sources` is called, since many simple operations don't
    need the full list of currently-installed config files.

.. _module_keys

keys
====

repolib.keys
    A :obj`dict` containing any installed repository signing keys on the system.
    This list is empty until :ref:`module_load_all_sources` is called, since 
    many simple operations don'tneed the full list of 
    currently-installed keys.

.. _module_compare_sources

compare_sources()
-----------------

repolib.compare_sources(source1, source2, excl_keys:list) -> bool
    Compares two sources based on arbitrary criteria.
    
    This looks at a given list of keys, and if the given keys between the two
    given sources are identical, returns True.
    
    Returns: :obj:`bool`
        `True` if the sources are identical, otherwise `False`.

source1, source2
^^^^^^^^^^^^^^^^
The two source objects to compare.

excl_keys
^^^^^^^^^
:obj:`list` A list of DEB822key names to ignore when comparing. Even if these  
items don't match, this function still returns true if all other keys match.

.. _module_combine_sources

combine_sources()
-----------------

repolib.combine_sources(source1, source2) -> None
    Copies all of the data in `source2` and adds it to `source1`.

    This avoids duplicating data and ensures that all of both sources' data are
    present in the unified source

source1
^^^^^^^
The source into which both sources should be merged

source2
^^^^^^^
The source from which to copy to `source1`


.. _module_url_validator

url_validator()
---------------

repolib.url_validator(url: str) -> bool
    Validates a given URL and attempts to see if it's a valid Debian respository
    URL. Returns `True` if the URL appears to be valid and `False` if not.

url
^^^
:obj:`str`The url to validate


.. _module_validate_debline

validate_debline()
==================

repolib.util.validate_debline(line: str) -> bool
    Validate if the provided debline ``line`` is valid or not. 

    Returns ``True`` if ``line`` is valid, otherwise ``False``.

line
^^^^
:obj:`str` The line to validate


.. _module_strip_hashes

strip_hashes()
--------------

repolib.strip_hashes(line: str) -> str
    Strips leading hash (`#`) characters from a line and returns the result.

line
^^^^
:obj:`str` The line to strip

.. _module_load_all_sources

load_all_sources()
------------------

repolib.load_all_sources() -> None

    Loads all sources from the current system configuration.


.. _module-set_testing

set_testing()
-------------

repolib.set_testing(testing: bool = True) -> None
    Enables or disables testing mode in Repolib

    When in testing mode, repolib will operate within a temporary directory 
    rather tan on your live system configuration. This can be used for testing 
    out changes to the program without worry about changes to the system config.
    It's also used for unit testing.


testing
^^^^^^^
:obj:`bool` - Wether testing mode should be enabled (`True`) or not (`False`)


Example
=======

The following code as a Python program that creates in ``example.sources`` file
in `/etc/apt/sources.list.d` with some sample data, then modifies the suites 
used by the source and prints it to the console, before finally saving the new,
modified source to disk::

    import repolib
    source = repolib.Source()
    file = repolib.SourceFile(name='example')

    source.ident = 'example-source'
    source.name = 'Example Source'
    source.types = [repolib.SourceType.BINARY]
    source.uris = ['http://example.com/software']
    source.suites = ['focal']
    source.components = ['main']
    file.add_source(source)

    print(source.ui)

    file.save()

When run with the appropriate arguments, it prints the contents of the source to 
console and then saves a new ``example.sources`` file::

    $
    example-source:
    Name: Example Source
    Enabled: yes
    Types: deb
    URIs: http://example.com/software
    Suites: focal
    Components: main

    $ ls -la /etc/apt/sources.list.d/example.sources
    -rw-r--r-- 1 root root 159 May  1 15:21 /etc/apt/sources.list.d/example.sources

Below is a walkthrough of this example.

Creating Source and File Objects
--------------------------------

The first step in using :ref:`repolib_module` is creating :ref:`source_object`
and :ref:`file_object`::

    source = repolib.Source()
    file = repolib.SourceFile(name='example')

The :ref:`source_object` will hold all of the information for the source to be 
created. The :ref:`file_object` represents the output file on disk, and allows 
for advanced usage like multiple sources per file.

Adding and Manipulating Data
----------------------------

The :ref:`source_object` contains attributes which describe the connfiguration 
aspects of the source required to fetch and install software. Generally, these 
attributes are lists of strings which describe different aspects of the source.
They can be set or retrieved like any other attributes::

    source.uris = ['http://example.com/software']
    source.suites = ['focal']

This will add a ``focal`` suite to our source and add a URI from which to 
download package lists.

:ref:`source_object` also presents a dict-like interface for setting and getting 
configuration data. Key names are case-insensitive and their order within the 
object are preserved. 

Adding the Source to the File
-----------------------------

Before the :ref:`source_object` can be saved, it needs to be added to a 
:ref:`file_object`::

    file.add_source(source)

This will add `source` to the `file`'s lists of sources, as well as setting the
`source`'s file attribute to `file`.

Saving Data to Disk
-------------------

Once a source has the correct data and has been added to a file object, it can 
be saved into the system configuration using :ref:`file-save`::

    file.save()

When called, this writes the sources stored in the file to disk. This does not 
destroy the object, so that it may be further manipulated by the program. 

.. note::
    While data within the source or file objects can be manipulated after 
    calling :ref:`file-save`, any subsequent changes will not be automatically
    written to disk as well. The :ref:`file-save` method must be called to 
    commit changes to disk.

.. _source_object:
