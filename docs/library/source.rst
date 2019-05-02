.. _source-object:

=============
Source object
=============

class repolib.Source (name='',enabled=True,types=[],uris=[],suites=[],components=[],options={},filename='example.source')
    Create a new :ref:`source-object`. All parameters should be passed as 
    keyword arguments. Each parameter has its own more detailed description 
    below, but in short they are:

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
        * :ref:`filename` - The filename to save the source to on disk. 
          (default: 'example.sources')

The following decribe how each of these are used. 

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

.. _filename:

filename
--------

This is a string value describing the filename to save the source to when using 
the :ref:`save-to-disk-method`. It defaults to ``example.sources``

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

Source.save_to_disk()
    Takes all of the current data saved in the :ref:`source-object` and writes 
    it to the disk. It uses the current :ref:`filename` attribute as the storage 
    location within ``/etc/apt/sources.list.d``. 


.. _load-from-file:

load_from_file()
----------------

Source.load_from_file(filename=None)
    Loads the source from a file on disk. The location loaded depends on the 
    :ref:`lff-filename` parameter's value, as described below:


.. _lff-filename:

filename
^^^^^^^^

The filename of the sources file to load from the disk. If ommitted, the method
instead loads from the current :ref:`filename` attribute, otherwise the method 
sets the :ref:`filename` attribute to the value of this argument. For example::

    >>> source = Source()
    >>> source.filename 
    'example.sources'
    >>> source.load_from_file(filename='google-chrome.sources')
    >>> source.filename 
    'google-chrome.sources'
    >>> source_with_name = Source()
    >>> source_with_name.filename = 'ppa-system76-pop.sources'
    >>> source_with_name.load_from_file()
    >>> source_with_name.filename
    'ppa-system76-pop.sources'

.. _set-source-enabled:

set_source_enabled()
--------------------

Source.set_source_enabled(is_enabled)
    This method can be used to quickly set the :ref:`source-object`.``types``
    attribute. Since the ``types`` attribute is a list of 
    :ref:`aptsourcetype-enum`s, this method can quickly set the type to either 
    of these values without needing to use the Enum directly. The argument
    :ref:`sse-is-enabled` is a boolean value.

.. _sse-is-enabled:

is_enabled
^^^^^^^^^^

If ``True``, the :ref:`source-object`.``types`` attribute is set to 
'[:ref:`aptsourcetype-enum`.BINARY, :ref:`aptsourcetype-enum`.SOURCE]'. 
Otherwise, it's set to '[:ref:`aptsourcetype-enum`.BINARY]' only.

