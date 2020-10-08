.. _ppa-object

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