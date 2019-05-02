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
feature parity with software-properties for most commonly used functions.

.. contents:: Table of Contents
   :local:

.. toctree::
    :maxdepth: 3
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
