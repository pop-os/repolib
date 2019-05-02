==========
Apt Manage
==========

``apt-manage`` is a command line tool for managing your local software sources
using RepoLib. Run ``apt-manage`` standalone to get a listing of all of the 
software repositories currently configured::

    $ apt-manage
    Current repositories:

    system
    pop_OS-apps
    pop_OS
    google-chrome

``apt-manage`` operates strictly on DEB822-style sources on your system; however, 
it can accept traditional "deb lines" and ``ppa:`` shortcuts as input to add a 
repository to your system. It also has the capability of converting legacy 
one-line sources into DEB822 sources.

.. toctree:: 
    :maxdepth 2
    :caption: apt-manage Documentation

    add
    repo
    source
    convert