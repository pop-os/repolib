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

*class repolib.**Source** (name='',enabled=True,types=[],uris=[],suites=[],components=[],options={},filename='example.source')*

    Create a new :ref:`source-object`. All parameters should be passed as 
    keyword arguments. Each parameter has its own more detailed description 
    below, but in short they are:

        * :ref:`name` - The human-readable name of the source. (default: '')
        * :ref:`enabled` - Whether the source is enabled or not at creation. 
          (default: True)
        * :ref:`types` - A list of the types that the source should use.
          (default: [])
        * :ref:'uris' - A list of URIs from which to fetch software or check for 
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

This field maps to the ``X-Repolib-Name:`` field in the .sources file, which 
is ignored by Apt and other standards-compliant sources parsers.