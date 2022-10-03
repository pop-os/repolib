.. _repolib-enums:

=============
RepoLib Enums
=============

RepoLib uses a variety of Enums to help ensure that data values are consistent 
when they need to be set to specific string values for compatibility. 

.. _enum_sourceformat

SourceFormat
============

repolib.SourceFormat()
    Encodes the two formats of source files, either ``.list`` for legacy format
    files or ``.sources`` for DEB822-formatted files.

    * ``DEFAULT`` - DEB822 formatting (value: ``"sources"``)
    * ``LEGACY`` - Legacy, one-line formatting (value: ``"list"``)


.. _enum_sourcetype

SourceType
==========

repolib.SourceType()
    Encodes the type of packages the repository provides (binary or source code).

    * ``BINARY`` - Binary package source type (value: ``"deb"``)
    * ``SOURCECODE`` - Source code package type (value : ``"deb-src"``)


.. _enum_aptsourceenabled:

AptSourceEnabled
================

repolib.AptSourceEnabled()
    Used to encode whether the source is enabled or not.

    * ``TRUE`` - The source should be enabled (value: ``"yes"``).
    * ``FALSE`` - The source should not be enabled (value: ``"no"``).
    