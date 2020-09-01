===================
Spec for apt-manage
===================

apt-manage is the CLI interface to manage software sources using RepoLib. It is
written in Python and shipped with RepoLib

Commands
========

There are several commands provided by apt-manage::

    add
    remove
    modify
    list
    source

add
---

The add command is used for adding new software sources to the system. It 
requires root. It has the following options::

    --disable, -d
    --source-code, -s
    --expand, -e

--disable
^^^^^^^^^

The --disable option (short form -d) will add the source and disable it 
immediately

--source-code
^^^^^^^^^^^^^

The --source-code option (short form -s) will enable source code for the 
new source as well as binary packages.

--expand
^^^^^^^^

The --expand options (short form -e) will show expanded details about the source
prior to adding it.

remove
------

The remove command will remove the selected source. It has no options. Note that
the system sources cannot be removed. This requires root.

modify
------

The modify command will allow making modifications to the specified repository.
It requires providing a repository to modify. It requires root. It accepts the
following options::

    --enable, -e
    --disable, -d
    --add-suite
    --remove-suite
    --add-component
    --remove-component
    --add-uri
    --remove-uri
    --add-option
    --remove-option

--enable
^^^^^^^^

The enable option (short form -e) sets the source to be enabled.

--disable
^^^^^^^^^

The disable option (short form -d) sets the source to be disabled.

--add-suite
^^^^^^^^^^^

The --add-suite option attempts to add the specified suite or suites to the 
source. If a given suite is already added to the source, it is ignored. Note 
that legacy deb sources cannot have multiple suites.

--remove-suite
^^^^^^^^^^^^^^

The --remove-suite option attempts to remove the specified suite or suites from
the source. If a given suite is not added to the source, it is ignored. The last
configured suite on a source cannot be removed.

--add-component
^^^^^^^^^^^^^^^

The --add-component option attempts to add the specified component or components
to the source. If a given component is already added to the source, it is
ignored.

--remove-component
^^^^^^^^^^^^^^^^^^

The --remove-component option attempts to remove the specified component or 
components from the source. If a given component is not added to the source, it
is ignored. The last configured component on a source cannot be removed.

--add-uri
^^^^^^^^^

The --add-uri option attempts to add the specified URI or URIs to the source. If
a given URI is already added to the source, it is ignored. Note that legacy deb
sources cannot have multiple URIs.

--remove-uri
^^^^^^^^^^^^

The --remove-uri option attempts to remove the specified URI or URIs from the
source. If a given URI is not added to the source, it is ignored. The last 
configured URI on a source cannot be removed.

--add-option
^^^^^^^^^^^^
The --add-option option attempts to add the given option or options as well as 
values to the source. If a given option is already added to the source, it is
ignored.

--remove-option
^^^^^^^^^^^^^^^

The --remove-option option attempts to remove the given option or options from
the source. If a given option isn't added to the source, it is ignored.

list
----

The list command lists available software sources as well as details about 
sources. With no further options, it lists all configured sources. With a 
configured source, it lists details about the specified source. It has the 
following option::

    --verbose, -v

--verbose
^^^^^^^^^

The --verbose option (short form -v) lists all details for all configured
software sources. It has no effect if a specific source is provided.

source
------

The source command allows enabling or disabling source code in configured 
sources. If a configured source is provided, this command will affect that 
source. If no sources are provided, this command will affect all sources on the 
system. Without options, it will list the status for source code packages. It
also accepts the following options, which require root::

    --enable, -e
    --disable, -d

--enable
^^^^^^^^

The --enable option (short form -e) will enable source code packages.

--disable
^^^^^^^^^

The --disable option (short form -d) will disable source code packages