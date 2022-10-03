.. _shortcuts

====================
Repository Shortcuts
====================

Repolib supports adding repositories via abbreviated shortcuts (such as
``ppa:system76/pop`` or ``popdev:master``) where the format of the shortcut is
given in the form of a prefix, and the data required to expand the shortcut into
a full repository is provided, with a colon character separating the two parts.
These function as subclasses of the :ref:`source_object` with specialized
functionality. Currently there is support for Launchpad PPAs and Pop_OS 
Development branches automatically.


Launchpad PPAs
==============

repolib.PPASource()
    RepoLib has built-in support for adding Launchpad PPA shortcuts, similarly to 
    ``add-apt-repository``. Launchpad shortcuts take the general form::

        ppa:owner-name/ppa-name

    If an internet connection is available, RepoLib can automatically fetch the 
    repository signing key as well as metadata like the description, human-readable
    name, etc.


Pop_OS Development Branches
===========================

repolib.PopdevSource()
    RepoLib can automatically add Pop_OS development branches for testing unstable
    pre-release software before it is ready for general use. Development branch 
    shortcuts take the form::

        popdev:branch-name

    If an internet connection is available, then RepoLib will also add the signing
    key for the branch (if it is not already added).



Adding Shortcut Repositories
============================

Shortcuts are generally added similarly to loading a different source from data,
the main difference being that in the call to :ref:`load_from_data` the only 
element in the ``data`` list should be a string of the shortcut::

    ppa_source = repolib.PPASource()
    ppa_source.load_from_data(['ppa:system76/pop'])

    popdev_source = repolib.PopdevSource()
    popdev_source.load_from_data(['popdev:master'])