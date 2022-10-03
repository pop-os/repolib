=====================
Managing Signing Keys
=====================

Signing keys are an important part of repository security and are generally
required to be used in repositories for all recent versions of APT. As previous
methods of handling Apt keys have been deprecated, Apt Manage provides easy
tools to use for managing signing keys for repositories in the ``key``
subcommand.

Most of the tools in the ``key`` subcommand are centered around adding a signing
key to a repository::

    apt-manage key repo-id --fingerprint 63C46DF0140D738961429F4E204DD8AEC33A7AFF

Apt Manage supports adding keys from a variety of sources:


Existing Keyring Files, --name, --path
======================================

``--name`` sets the :ref:`signed_by` value of the existing repository to the 
name of a file within the system key configuration directory::

    apt-manage key popdev-master --name popdev

``--path`` sets the :ref:`signed_by` value of the existing repository to the 
path of a file on disk::

    apt-manage key popdev-master --path /etc/apt/keyrings/popdev-archive-keyring.gpg


Keyring Files Stored on the Internet, --url
===========================================

``--url`` will download a key file from the internet and install it into the 
system, then set the repository to use that key::

    apt-manage key popdev-master --url https://example.com/sigining-key.asc


Keys Stored on a Public Keyserver
=================================

``--fingerprint`` will fetch the specified fingerprint from a public keyserver.
By default, keys will be fetched from ``keyserver.ubuntu.com``, but any SKS 
keyserver can be specified using the ``--keyserver=`` argument::

    apt-manage key ppa-system76-pop \
        --fingerprint=E6AC16572ED1AD6F96C7EBE01E5F8BBC5BEB10AE
    
    apt-manage key popdev-master \
        --fingerprint=63C46DF0140D738961429F4E204DD8AEC33A7AFF \
        --keyserver=https://keyserver.example.com/


Adding ASCII-Armored Keys Directly, --ascii
===========================================

``--ascii`` Will take plain ascii data from the command line and add it to a new
keyring file, then set the repository to use that key::
    
    apt-manage key popdev-master --ascii "$(/tmp/popdev-key.asc)"


Removing Keys
=============

Generally, manually removing keys is not necessary because removing a source 
automatically removes the key (if it is the only source using that key). However,
If there is a need to remove a key manually (e.g. the signing key has changed 
and must be re-added), then removal is supported::

    apt-manage key popdev-master --remove

This will remove the key from the repository configuration and if no other 
sources are using a particular key, it will also remove the keyring file from 
disk. 
