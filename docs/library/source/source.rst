.. _source-object:

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

class repolib.Source (ident='', filename='')
    Create a new :ref:`source-object`. All parameters should be passed as 
    keyword arguments. Each parameter has its own more detailed description 
    below, but in short they are:

        * :ref:`ident` - The system-identifier to use for this source.
        * :ref:`filename` - The filename to save to on disk.
    
    The following additional attributes are also specified:

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
        * :ref:`options` - Optional items affecting the source. (default: {})

The following decribe how each of these are used. 

.. _ident:

ident
-----

The ``ident`` is the system-identifier for this source. This determines the 
filename the source will use on-disk as well as the way to specify a source to 
load. 

.. _filename:

filename
--------

The ``filename`` is an alternate method to specify the ident, and is retained 
for backwards compatibility with RepoLib 1.0.x. If the filename is specified, 
any ``.list`` or ``.source`` suffixes are stripped, then the name is saved as 
the :ref:`ident` attribute.

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

.. _options:

options
-------

This is a dictionary containing key value pairs of options to add to the source. 
Options often are used to restrict a source to certain CPU architectures or 
languages. Valid options include:

    * ``Architectures``
    * ``Languages``
    * ``Targets``
    * ``PDiffs``
    * ``By-Hash``

=======
Methods
=======

.. _make-source-string:

make_source_string()
--------------------

Source.make_source_string()
    Takes the data from the :ref:`source-object` and makes it a printable string 
    for output to console or for saving to a file. The :ref:`save-to-disk` 
    method uses this method as a basis for its file output.

.. note::
    The ``Name:`` field output by this method is not suitable for directly 
    saving to a file without additional processing. When using this method to 
    generate data for manually saving to disk, be sure to replace ``Name:`` with 
    ``X-Repolib-Name:`` first.

.. _save-to-disk:

save_to_disk() 
--------------

Source.save_to_disk(save=True)
    Takes all of the current data saved in the :ref:`source-object` and writes 
    it to the disk. It uses the current :ref:`filename` attribute as the storage 
    location within ``/etc/apt/sources.list.d``. 
    
    The ``save`` parameter affects whether the source is actually saved or not.
    This is useful in some subclasses.

.. _load-from-file:

load_from_file()
----------------

Source.load_from_file(filename=None, ident=None)
    Loads the source from a file on disk. The location loaded depends on the 
    :ref:`lff-filename` and :refF`lff-ident` parameter's value, as described 
    below:

.. _lff-ident:

ident
^^^^^

The ident of the source to load from the disk. If omitted, load from the 
specified filename or the the current :ref:`ident` attribute. If provided, this
method will set the :ref:`ident` attribute. For example::

    >>> source = Source()
    >>> source.filename 
    'example.sources'
    >>> source.load_from_file(ident='google-chrome')
    >>> source.ident 
    'google-chrome'
    >>> source_with_name = Source()
    >>> source_with_name.ident = 'ppa-system76-pop'
    >>> source_with_name.load_from_file()
    >>> source_with_name.ident
    'ppa-system76-pop'

.. _lff-filename:

filename
^^^^^^^^

The ident of the source to load from the disk. If omitted, load from the 
specified filename or the the current :ref:`ident` attribute. If provided, this
method will set the :ref:`ident` attribute. For example::

    >>> source = Source()
    >>> source.filename 
    'example.sources'
    >>> source.load_from_file(filename='google-chrome.sources')
    >>> source.ident 
    'google-chrome'
    >>> source_with_name = Source()
    >>> source_with_name.ident = 'ppa-system76-pop'
    >>> source_with_name.load_from_file()
    >>> source_with_name.ident
    'ppa-system76-pop'

.. _make_source_string:

make_source_string()
--------------------

Source.make_source_string()
    This method returns a string-representation of the source. Note that this 
    method is intended for user-facing output. If you need the string data as 
    it will be written to disk, use the ``Source.dump()`` method instead.

.. _set-source-enabled:

set_source_enabled()
--------------------

Source.set_source_enabled(is_enabled)
    This method can be used to quickly set the :ref:`source-object`.``types``
    attribute. Since the ``types`` attribute is a list of 
    :ref:`aptsourcetype-enum` values, this method can quickly set the type to 
    either of these values without needing to use the Enum directly. The 
    argument :ref:`sse-is-enabled` is a boolean value.

.. _sse-is-enabled:

is_enabled
^^^^^^^^^^

If ``True``, the :ref:`source-object` ``types`` attribute is set to 
[:ref:`aptsourcetype-enum`.BINARY, :ref:`aptsourcetype-enum`.SOURCE]. 
Otherwise, it's set to [:ref:`aptsourcetype-enum`.BINARY] only.

.. _copy:

copy()
------

Source.copy(source_code=True)
    Copies the source and returns an identical source object to the current 
    source. This is useful for legacy one-line sources to create copies of 
    sources with all data identical to the first source. 
  
.. _c-source-code:

source_code
^^^^^^^^^^^

If ``True``, the returned Source will be identical except that the :ref:`types`
attribute will be set equal to ``['deb-src']`` instead of the current value.

.. _make-name:

make_name()
-----------

Source.make_name(prefix='')
    Creates a name for the source, with the optional ``prefix`` specified. If a 
    ``prefix`` is specified, it will be appended to the name with a ``-``
    character separating the prefix from the generated name. 

.. _init-values:

init_values()
-------------

Source.init_values()
    Initializes the Source's attributes with default data in-order. This is 
    recommended to ensure that the fields in the underlying deb822 Dict are 
    in order.

.. _make-debline:

make_debline()
--------------

Source.make_debline()
    Returns a one-line style source line for this source. If the :ref:`uris`, 
    :ref:`suites`, or :ref:`types` fields contain more than a single value, the 
    output will raise a ``SourceError`` exception, since one-line sources can 
    only contain one of these different types.
