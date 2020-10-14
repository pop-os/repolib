.. _util-module

===================
repolib.util Module
===================

The ``util`` Module contains several useful helper functions and attributes 
which may be helpful to developers writing applications using RepoLib.


.. _util-sources-dir:

SOURCES_DIR
===========

repolib.util.SOURCES_DIR
    The current value of the location of the sources files on the system. The 
    default value for this attribute is``/etc/apt/sources.list.d``


.. _util-testing:

TESTING
=======

repolib.util.TESTING
    Stores the current state of the module's testing mode. 


.. _util-distro-codename:

DISTRO_CODENAME
===============

repolib.util.DISTRO_CODENAME
    The current CODENAME field from LSB. If LSB is not available, it will 
    default to ``linux``.


.. _util-clean-chars

CLEAN_CHARS
===========

repolib.util.CLEAN_CHARS 
    A ``dict`` which maps invalid characters for the :ref:`ident` attributes 
    which cannot be used and their replacements. These limitations are based on 
    invalid characters in unix-compatible filenames.


.. _util-get-source-path

url_validator()
===============

repolib.util.url_validator(url):
    Validates ``url`` to tell whether it is a malformed URI or not. If it is 
    valid, returns ``True``. Otherwise, returns ``False``

get_source_path()
=================

repolib.util.get_source_path(ident, log=None)
    Tries to get the full path to the source with ident ``ident``. Optionally, 
    include a ``logging.log`` object for logging output.

    Returns a ``pathlib.Path`` object for the path to the requested source.


.. _util-get-sources-dir:

get_sources_dir()
=================

repolib.util.get_sources_dir(testing=False)
    Gets the path to the current sources dir. 

    If ``testing`` is ``True``, then update the current value of 
    :ref:`util-testing` to ``True`` and the value of :ref:`util-sources-dir` to 
    ``'/tmp/repolib_testing'``

    Returns a ``str`` of the current :ref:`util-sources-dir`.

.. _util-validate-debline

validate_debline()
==================

repolib.util.validate_debline(line)
    Validate if the provided debline ``line`` is valid or not. 

    Returns ``True`` if ``line`` is valid, otherwise ``False``.
    