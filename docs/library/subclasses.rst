.. _source-subclasses:

===================
Source() Subclasses
===================

There are a variety of subclasses of the :ref:`repolib-module` 
:ref`source-object` class which tailor its functionality toward dealing with 
specific types of parent sources. The default :ref`source-object` is best for 
dealing with native DEB822 sources on disk or as entered by user input. 


.. _system-source-object:

SystemSource()
==============

class repolib.SystemSource()
    A special :ref:`source-object` with its ``filename`` attribute pre-set to 
    the path of the system software sources file. It is otherwise identical to 
    the main :ref:`source-object` class.


.. _deb-source-object:

DebLine()
=========

class repolib.DebLine(line)
    A :ref:`source-object` class specifically intended to parse one-line debian 
    repository list entries. This can be useful for both converting legacy 
    sources to the new format, as well as a simple way for a user to add a new 
    software source, since this format can be copy-pasted as a full line. 

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

PPALine()
=========

class repolib.PPALine(line)
    A :ref:`source-object` with convenience features for adding or removing PPA 
    sources from launchpad.net. This class will exapand a ``ppa:owner/source`` 
    format entry into a complete repository, and will download and save the 
    signing key for the repository automatically (if an internet connection is 
    available). It will also automatically name the entry based on data 
    available on Launchpad.

    *:ref:`ppaline-line` - The ``ppa:`` formatted entry to add.

.. _ppaline-line:

line
----

A repository to add in the format::

    ppa:onwer-name/repository-name

This will be automatically expanded to the uri 
``http://ppa.launchpad.net/owner-name/repository-name/ubuntu` and will be added 
with the current OS version codename serving as the "Suite:" and "main" as the 
only component. 


.. _ppaline-methods:

PPALine() Methods
-----------------

.. _load-from-ppa:

load_from_ppa()
^^^^^^^^^^^^^^^

PPALine.load_from_ppa(ppa_line=None)
    Loads source information from launchpad about the ppa described by the 
    :ref:`ppa-ppa-line` argument, or from the PPALine.ppa_line attribute if 
    blank. 

    * :ref:`ppa-ppa-line` - The PPA to load from Launchpad.


.. _ppa-ppa-line:

ppa_line
""""""""

PPAs are formatted as ``ppa:onwer-name/repository-name``. This argument if 
present, must be a string matching this format.


.. _ppa-save-to-disk:

save_to_disk()
^^^^^^^^^^^^^^

PPALine.save_to_disk()
    Fetches the signing key for the repository from the Ubuntu keyserver, then 
    adds it to the system. It then loads the standard :ref:`source-object` 
    :ref:`save-to-disk` method to save the repository information to the system 
    sources.


_ppa-module-functions:

repolib.ppa Module functions
============================

The module containing the :ref:`ppa-source-object` class also contains two 
public helper functions that can be helpful in manual processing of the data for 
a :ref:`ppa-source-object`. 


.. _get-info-from-lp:

get_info_from_lp()
^^^^^^^^^^^^^^^^^^

repolib.ppa.get_info_from_lp(owner_name, ppa)
    Requests PPA information from Launchpad and returns a Dict containing the 
    JSON response. 

    * ``owner_name`` - The user or team name which hosts the PPA on launchpad.
    * ``ppa`` - The name of the ppa for which to fetch information. 

.. _add-key:

add_key()
^^^^^^^^^

repolib.ppa.add_key(fingerprint)
    Downloads the key with ``fingerprint`` from keyserver.ubuntu.com and adds it 
    to the system configuration. 

    * ``fingerprint`` - The fingerprint of the key to download and fetch. This 
      value is present in the JSON data returned by :ref:`get-info-from-lp`
      function.


.. _system-source-object:

SystemSource()
==============

class repolib.SystemSource()
    A standard :ref:`source-object` with the filename pre-set to the path for 
    system software sources. It otherwise operates identically to the standard 
    :ref:`source-object` class.


