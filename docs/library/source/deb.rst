.. _deb-source-object:

DebLine()
=========

class repolib.DebLine(line)
    A :ref:`source-object` class specifically intended to parse one-line debian 
    repository list entries. This can be useful for both converting legacy 
    sources to the new format, as well as a simple way for a user to add a new 
    software source, since this format can be copy-pasted as a full line. 

    LegacyDeb Classes contain one ``DebLine()`` source for each different line
    in the source file.

    * :ref:`debline-line` - The one-line source entry to parse into DEB822 format.


.. _debline-line:

line
----

This is the one-line repository entry to operate on. Because this line contains 
the necessary information to fill in the :ref:`source-object` data completely, 
it is the only argument that the :ref:`deb-source-object` accepts. 

The line parameter is a string and *must* follow this format::

    deb|deb-src ([options,...]) uri suite components


.. _ppa-source-object: