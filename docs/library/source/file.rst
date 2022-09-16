.. _file_object:

===========
File object
===========

SourceFile objects are the interface between the OS storage and the repolib
:ref:`source_object` items. Files contain sources and comments and allow for 
loading sources from and saving them to disk. They also assign idents to sources
in a way that ensures each source has a unique ident. 

Attributes
==========

File objects contain the following attributes:

.. _file-name

name
----

SourceFile.name
    The name of the file on disk. This does not include the file extension, as 
    that is stored in :ref:`file-format`.

.. _file-path

path
----

SourceFile.path
    A ``Pathlib.Path`` object representing this file's actual path on disk. Note 
    that the file may not actually exist on disk yet.

.. _file-format

format
------

SourceFile.format
    The format this file should be saved in. Saved as a :ref:`enum_sourceformat`.

.. _file-contents

contents
--------

SourceFile.contents
    A :obj:`list` containing, in order, every comment line and source in this 
    file.

.. _file-sources

sources
-------

SourceFile.sources
    A :obj:`list` containing, in order, only the sources in this file.


Methods
=======

.. _file-add_source

add_source()
------------

SourceFile.add_source(source) -> None
    Adds a given source to the file. This correctly appends the source to both  
    the :ref:`file-contents` and :ref:`file-sources` lists, and sets the 
    :ref:`source-file` attribute of the source to this file.

source
^^^^^^
The source to add to the file.

.. _file-remove_source

remove_source()
---------------

SourceFile.remove_source(ident: str) -> None
    Removes the source with a specified ident from this file. 

ident
^^^^^
The ident of the source to remove from the file.

.. _file-get_source_by_ident

get_source_by_ident()
---------------------

SourceFile.get_source_by_ident(ident: str) -> :obj:`Source`
    Finds a source within this file given a specified ident and returns the 
    :ref:`source_object` matching that ident. If the file does not contain a 
    Source matching the given ident, raises a :ref:`exc_sourcefileerror`.

ident
^^^^^
The ident to look up.

.. _file-reset_path

SourceFile.reset_path() -> None
    Attempts to detect the full path to the file given the :ref:`file-name`
    attribute for this file. If the ``name.sources`` exists on disk, the path 
    will be set to that, otherwise if the ``name.list`` exists, it will be set
    to that instead. Failing both, the path will fallback to ``name.sources`` as
    a default.

.. _file-load

load()
------

SourceFile.load() -> None
    Loads the file specified by :ref:`path` from disk, creating sources and 
    comments and appending them in order to the :ref:`file-contents` and 
    :ref:`file-sources` lists as appropriate. 

.. _file-save

save()
------

SourceFile.save() -> None
    Saves the file and any sources currently configured to disk. This method 
    must be called to commit changes to disk. If the file currently contains no
    sources, then the file will instead be deleted. 


Output
======

There are four attributes which contain the output of the files stored as 
strings and which are ready for full output in the specified format. 

.. _file-deb822

deb822
------

SourceFile.deb822
    Outputs the entire file as DEB822-formatted sources

.. _file-legacy

legacy
------

SourceFile.legacy
    Outputs the entire file as one-line legacy-formatted deb lines

.. _file-ui

ui
--

SourceFile.ui
    Outputs the file in a format for output through a UI (e.g. for preview or
    external parsing.)

.. _file-output

output
------

SourceFile.output
    Outputs the entire file in the format matching that configured in 
    :ref:`file-format`. 
