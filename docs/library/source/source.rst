.. _source_object:

=============
Source object
=============

The Source object is the base class for all of the sources used within RepoLib.
The Source class itself is a subclass of the deb822() class from the Python 
Debian module, which provides a dict-like interface for setting data as well as 
several methods for dumping data to files and other helpful functions.

.. toctree::
    :maxdepth: 2
    :caption: Source

    deb
    legacy-deb
    ppa-object
    system

class repolib.Source (file=None)
    Create a new :ref:`source_object`. 

    
    The Source object has the following attributes:

        * :ref:`ident` - The system-identifier to use for this source.
        * :ref:`name` - The human-readable name of the source. (default: '')
        * :ref:`enabled` - Whether the source is enabled or not at creation. 
          (default: True)
        * :ref:`types` - A list of the types that the source should use.
          (default: [])
        * :ref:`uris` - A list of URIs from which to fetch software or check for 
          updates. (default: [])
        * :ref:`suites` - Suites in which to narrow available software. (default: 
          [])
        * :ref:`components` - Components of the source repository to enable. 
          (default: [])
        * :ref:`signed_by` - The path to the signing key for this source
        * :ref:`file` - The :ref:`file_object` for this source
        * :ref:`key` - The :ref:`key_object` for this source.
        * :ref:`twin_source`: - This source should be saved with both binary and
          source code types enabled.

The following decribe how each of these are used. 

.. _ident:

ident
-----

The ``ident`` is the system-identifier for this source. This determines the 
filename the source will use on-disk as well as the way to specify a source to 
load. 

.. _name:

name
----

This is a human-readable and nicely-formatted name to help a user recognize
what this source is. Any unicode character is allowed in this field. If a 
source is opened which doesn't have a name field, the filename will be used.

:ref:`name` is a string value, set to ``''`` by default. If there is no name in 
a loaded source, it will be set to the same as the filename (minus the 
extension).

This field maps to the ``X-Repolib-Name:`` field in the .sources file, which 
is ignored by Apt and other standards-compliant sources parsers.

.. _enabled:

enabled
-------

Apt sources can be disbaled without removing them entirely from the system. A 
disabled source is excluded from updates and new software installs, but it can 
be easily re-enabled at any time. It defaults to ``True``.

This field maps to the ``Enabled:`` field in the .sources file. This is optional 
per the DEB822 standard, however if set to anything other than ``no``, the 
source is considered enabled.

.. _types:

types
-----

Debian archives may contain either binary packages or source code packages, and 
this value specifies which of those Apt should look for in the source. ``deb`` 
is used to look for binary packages, while ``deb-src`` looks for source code 
packages. RepoLib stores this value as a list of :ref:`aptsourcetype-enum`s, and 
defaults to ``[AptSourceType.BINARY]``.

This field maps to the ``Types:`` field in the sources file. 

.. _uris:

uris
----

A list of string values describing the URIs from which to fetch package lists 
and software for updates and installs. The currently recognized URI types are:

    * file
    * cdrom
    * http
    * ftp
    * copy
    * rsh
    * ssh

DEB822 sources may directly contain an arbitrary number of URIs. Legacy sources 
may also have multiple URIs; however, these require writing a new deb line for 
each URI as the one-line format only allows a single URI per source.

.. note::
    Although these are the currently-recognized official URI types, Apt can be 
    extended with additional URI schemes through extension packages. Thus it is 
    **not** recommended to parse URIs by type and instead rely on user input 
    being correct and to throw exceptions when that isn't the case.

.. _suites:

suites
------

The Suite, also known as the **distribution** specifies a subdirectory of the 
main archive root in which to look for software. This is typically used to 
differentiate versions for the same OS, e.g. ``disco`` or ``cosmic`` for Ubuntu, 
or ``squeeze`` and ``unstable`` for Debian. 

DEB822 Sources allow specifying an arbitrary number of suites. One-line sources 
also support multiple suites, but require an additional repo line for each as 
the one-line format only allows a single suite for each source.

This value maps to the ``Suites:`` field in the sources file. 

.. _components:

components
----------

This value is a list of strings describing the enabled distro components to 
download software from. Common values include ``main``, ``restricted``, 
``nonfree``, etc.

.. _signed_by

signed_by
---------
The path to the keyring containing the signing key used to verify packages 
downloaded from this repository. This should generally match the 
:ref:`key-path` attribute for this source's :ref:`key` object.

.. _source-file

file
----
The :ref:`file_object` for the file which contains this source. 

.. _key

key
---
The :ref:`key_object` for this source.

=======
Methods
=======


.. _get_description

Source.get_description() -> str
    Returns a :obj:`str` containing a UI-compatible description of the source. 

.. _reset_values:

reset_values()
-------------

Source.reset_values()
    Initializes the Source's attributes with default data in-order. This is 
    recommended to ensure that the fields in the underlying deb822 Dict are 
    in order and correctly capitalized.

.. _load_from_data

load_from_data()
----------------

Source.load_from_data(data: list) -> None
    Loads configuration information from a list of data, rather than using 
    manual entry. The data can either be a list of strings with DEB822 data, or
    a single-element list containing a one-line legacy line.

data
^^^^
The data load load into the source. If this contains a legacy-format one-line 
repository, it must be a single-element list. Otherwise, it should contain a 
list of strings, each being a line from a DEB822 configuration.

.. _generate_default_ident

generate_default_ident()
------------------------

Source.generate_default_ident(prefix: str = '') -> str
    Generates a suitable default ident, optionally with a prefix, and sets it. 
    The generated ident is also returned for processing convenience.

prefix
^^^^^^
The prefix to prepend to the ident.

.. _generate_default_name

generate_default_name()
_______________________

Source.generate_default_name() ->
    Generates a default name for the source and sets it. The generated name is
    also returned for convenience.

.. _load_key

load_key()
__________

Source.load_key(ignore_errors: bool = True) -> None
    Finds the signing key for this source spefified in :ref:`signed_by` and 
    loads a :ref:`key_object` for it. 

ignore_errors
^^^^^^^^^^^^^
If `False`, raise a :ref:`exc_sourceerror` if the key can't be loaded or doesn't
exist.

.. _source_save

save()
------

Source.save()
    Proxy method for the :ref:`file-save` method for this source's 
    :ref:`file_object`.

Output Properties
=================

There are three output properties which contain the current source data for 
output in a variety of formats.

.. _source_deb822

deb822
------

Source.deb822
    A representation of the source data as a DEB822-formatted string

.. _source_legacy

legacy
------

Source.legacy
    A one-line formatted string of the source. It :ref:`twin_source` is ``True``,
    then there will additionally be a ``deb-src`` line following the primary 
    line.

.. _source_ui

ui
--

Source.ui
    A representation of the source with certain key names translated to better
    represent their use in a UI for display to a user.
