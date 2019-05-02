.. RepoLib documentation master file, created by
   sphinx-quickstart on Wed May  1 13:49:01 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to RepoLib's documentation!
===================================

RepoLib is a Python library and CLI tool-set for managing your software 
system software repositories. It's currently set up to handle APT repositories
on Debian-based linux distributions. 

RepoLib is intended to operate on DEB822-format sources. It aims to provide
feature parity with software-properties for most commonly used functions. It 
also allows for simple, automated conversion from legacy "one-line" style 
source to newer DEB822 format sources. These sources will eventually 
deprecate the older one-line sources and are much easier to parse for both 
human and machine. For a detailed explanation of the DEB822 Source format, see
:ref:`deb822-explanation`.

RepoLib provides much faster access to a subset of ``SoftwareProperties`` 
features than ``SoftwareProperties`` itself does. Its scope is somewhat more 
limited because of this, but the performance improvements gained are substantial.
``SoftwareProperties`` also does not yet feature support for  managing DEB822 
format sources, and instead only manages one-line sources. 

RepoLib is available under a BSD 2-Clause License. Full License below

.. include: ../LICENSE

.. contents:: Table of Contents
   :local:

.. toctree::
    :maxdepth: 4
    :caption: Developer Documentation

    library/developer

.. toctree::
    :maxdepth: 1
    :caption: RepoLib Documentation

    installation

.. toctree:: 
    :maxdepth: 1
    :caption: apt-manage Documentation

    aptmanage/aptmanage
