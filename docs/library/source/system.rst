.. _system-source-object:

SystemSource()
==============

class repolib.SystemSource()
    A special :ref:`source-object` with its ``ident`` attribute pre-set to 
    the path of the system software sources file. It also contains a 
    ``default_mirror`` attribute for storing the OS Vendor recommended mirror,
    and a method to reset the current ``URIs`` to the given default.


.. _system-default-mirror

default_mirror
==============

Contains the OS Vendor's recommended default mirror for downloading software.


.. _system-set-default-mirror

set_default_mirror()
====================

repolib.SystemSource.set_default_mirror()
    Sets the System Source URIs to the one in the :ref:`system-default-mirror`
    attribute. Note that this does not save the source; you still need to call 
    :ref:`save-to-disk` to save the changes.
    