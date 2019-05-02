=========================
Converting Legacy Sources
=========================

RepoLib and Apt-Manage is intended to operate strictly with DEB822-style 
sources. Some software may automatically add or modify existing one-line sources 
within your system configuration. Because of this, Apt-Manage includes a 
conversion utility to automatically generate DEB822 sources from any active 
one-line sources in your system configuration. ::

    $ sudo apt-manage convert

This will create back-ups of any third-party source files present on your system 
and then convert to the new format. For extra insurance against loss of data, 
Apt-Manage will not delete any files, but will disable sources in any ``.list`` 
files it converts. If you need to revert to the one-line files, you can rename 
the relevant ``.save`` file to end in ``.list`` instead, then modify to file to 
uncomment any required sources. Be sure to disable the source first, or you may 
get warnings about sources configured in multiple locations.

.. warning::
    While every attempt has been made to ensure the process will not result in 
    data loss, converting your sources automatically may cause problems. Back 
    up your data and sources lists before attempting automatic conversion, or 
    convert your sources manually.

Apt-Manage will offer to convert both third-party sources in 
``/etc/apt/sources.list.d`` as well as system sources configured in 
``/etc/apt/sources.list``. It will also offer a preview of the converted source 
which you can use to verify that the source is correctly converted. If anything 
looks wrong with that source, deny the changes and then manually convert the 
source instead.
