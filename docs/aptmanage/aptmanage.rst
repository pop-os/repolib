==========
Apt Manage
==========

``apt-manage`` is a command line tool for managing your local software sources
using RepoLib. Run ``apt-manage`` standalone to get a listing of all of the 
software repositories currently configured::

    $ apt-manage
    Configured sources:
    system 
    pop-os-apps
    ppa-system76-pop 


``apt-manage`` operates on both DEB822-formated sources (located in the
``/etc/apt/sources.list.d/*.sources`` files) as well as using traditional
one-line format sources (in ``/etc/apt/sources.list.d/*.list`` files). 

.. toctree:: 
    :maxdepth 1
    :caption: apt-manage Documentation

    add
    list
    modify
    remove
    key
