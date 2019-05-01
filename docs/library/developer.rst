.. _repolib-module:

=====================
RepoLib Python Module
=====================

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
        uris=['http://example.com/ubuntu'], suites=['disco'],
        components=['main'], options={'Architectures': ['amd64', 'armel']}
    )
    
    source.suites.append('cosmic')
    
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

The first step in using :ref:`repolib-module` is creating a :ref:`source-object` 
object::

    source = repolib.Source(
        filename='example.sources',
        name='Example Source', enabled=True, types=['deb', 'deb-src'],
        uris=['http://example.com/ubuntu'], suites=['disco'],
        components=['main'], options={'Architectures': ['amd64', 'armel']}
    )

The :ref:'source-object' object will 

.. _source-object: