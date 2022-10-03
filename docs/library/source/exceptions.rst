.. _exceptions

==========
Exceptions
==========

RepoLib throws various forms of exceptions to halt execution of code when 
incorrect input is detected or deviations from expected norms are encountered.

.. _exc_repoerror

RepoError()
-----------

Repolib.RepoError()
    This is base exception thrown by RepoLib. All other exceptions are
    subclasses of this exception type.

.. _exc_sourceerror

SourceError()
-------------

Repolib.Source.SourceError()
    Raised when errors result from processing within the :obj:`source_object` or
    one of it's subclasses.

.. _exc_debparseerror

DebParseError()
---------------

Repolib.parsedeb.DebParseError()
    Raised due to problems parsing legacy Debian one-line repository lines.

.. _exc_sourcefileerror

SourceFileError()
-----------------

Repolib.file.SourceFileError()
    Raised due to errors handling :ref:`file_object` objects.

.. _exc_keyfileerror

KeyFileError()
--------------

Repolib.key.KeyFileError()
    Raised due to errors loading/finding key files or :ref:`key_object` objects.
