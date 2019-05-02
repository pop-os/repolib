.. _repolib-enums:

=============
RepoLib Enums
=============

RepoLib uses a variety of Enums to help ensure that data values are consistent 
when they need to be set to specific string values for compatibility. 

.. _aptsourcetype-enum:

AptSourceType
=============

repolib.AptSourceType()
    Used to encode the type of packages to fetch from the archive; either binary 
    or source code. The values for this enum are below:

    * ``BINARY`` - Binary package source type (value: ``"deb"``).
    * ``SOURCE`` - Source code package type (value : ``"deb-src"``).