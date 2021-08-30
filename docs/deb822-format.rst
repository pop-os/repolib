.. _deb822-explanation:

=======================================
Explanation of the DEB822 Source Format
=======================================

The sources described in ``/etc/apt/sources.list.d/`` on a Debian-based OS are 
designed to support any number of different active and inactive sources, as well 
as a large variety of source media and transport protocols. The files describe
one or more sources each and contain multiline stanzas defining one or more 
sources per stanza, with the most preferred source listed first. Information 
about available packages and versions from each source is fetched using the 
``apt update`` command, or with an equivalent command from a different frontend.


.. _sources-list-d:

sources.list.d
==============

APT source information is stored locally within the ``/etc/apt/sources.list.d`` 
directory. In this directory are one or more files describing one or more 
sources each. For :ref:`deb822-format` sources, each file needs to have the .sources 
extension. The filenames may only contain letters, digits, underscore, hyphen, 
and period characters. Files with other characters in their filenames will cause 
APT to print a notice that it has ignore that file (unless the file matches a 
pattern in the ``Dir::Ignore-Files-Silently`` configuration list, which will 
force APT to silently ignore the file.


.. _one-line-format:

One-Line-Style Format
=====================

In order to understand some of the decisions behind using the :ref:`deb822-format`
sources, it is helpful to understand the older :ref:`one-line-format`.

:ref:`one-line-format` sources occupy one line in a file ending in ``.list``. 
The line begins with a type (i.e. ``deb`` or ``deb-src`` followed by options and 
arguments for this type. Individual entries cannot be continued onto multiple 
lines (hence the "one-line" portion of this format's name). Empty lines in 
``.list`` files are ignored, and a ``#`` character anywhere on the line signifies
that the remainder of that line is a comment. Consequently an entry can be 
disabled by commenting out that entire line (prefixing it with a ``#``). If 
options are provided, they are space-separated and all together are enclosed 
within square brackets ( ``[]`` ). Options allowing multiple values should 
separate each value with a comma ( ``,`` ) and each option name is separated 
from its values by an equals sign ( ``=`` ).

This is the traditional format and is supported by all current APT versions. 
It has the advantage of being relatively compact for single-sources and 
relatively easy for humans to parse. 


.. _one-line-disadvantages:

Disadvantages
-------------

Problems with the :ref:`one-line-format` begin when parsing entries via machine. 
Traditional, optionless entries are relatively simple to parse, as each 
different portion of the entry is separated with a space. With options, however, 
this is no longer the case. The presence of options causes there to be no, 1, or 
multiple segments of configuration between the type declaration and the URI. 
Additionally, APT sources support a variety of URI schemas, with the capability 
for extensions to add additional schemas on certain configurations. Thus, 
supporting modern, optioned :ref:`one-line-format` source entries requires use 
of either regular expressions or multi-level parsing in order to adequately 
parse the entry. Further compounding this support is the fact that 
:ref:`one-line-format` entries can have one or more components, preventing 
parsing of sources backwards from the end towards the front. 

Consider the following examples::

    deb [] http://example.com.ubuntu disco main restricted multiverse universe
    deb [ arch=amd64 ] http://example.com/ubuntu disco main nonfree
    deb [lang=en_US] http://example.com/ubuntu disco main restricted universe multiverse
    deb [ arch=amd64,armel lang=en_US,en_CA ] http://example.com/ubuntu disco main

Each of these entries are syntactically valid source entries, each cleanly 
splits into eight segments when splitting on spaces. Depending on which entry 
being parsed, the URI portion of the entry may be in index 2, 4, or 5 while 
options (where present) may be in index 1, 2, or 3. If we want to work backwards, 
then the URI is in either index -3, -4, or -6. The only segments guaranteed to 
be present at any given index is the type. The situation is even more 
complicated when considering that entries may have at a minimum 3 elements, and
at a maximum 12 or more elements.

In addition to parsing difficulty, :ref:`one-line-format` entries may only 
specify a single suite and URI per entry, meaning that having two active mirrors 
for a given source requires doubling the number of entries configured. You must 
also create an extra set of duplicated entries for each suite you want to 
configure. This can make tracking down duplicated entries difficult for users
and leads to longer-than-necessary configuration.


.. _deb822-format:

Deb822-style Format
===================

This format addresses the file-length, duplication, and machine-parsability 
issues present in the :ref:`one-line-format`. Each source is configured in a 
single stanza of configuration, with lines explicitly describing their 
function for the source. They also allow for lists of values for most options, 
meaning that mirrors or multiple suites can be defined within a single source. A
``#`` character at the beginning of a line marks the entire line as a comment. 
Entries can again be disabled by commenting out each line within the stanza;
however, as a convenience this format also brings an ``Enabled:`` field which, 
when set to ``no`` disables the entry as well. Removing this field or setting it 
to ``yes`` re-enables it. Options have the same format as every other field, 
thus a stanza may be parsed by checking the beginning of each line for a fixed 
substring, and if the line doesn't match a known substring, it can be assumed 
the line is an option and the line can be ignored. Unknown options are ignored 
by all versions of APT. This has the unintentional side effect of adding 
extensibility to the source; by selecting a carefully namespaced field name, 
third-party applications and libraries can add their own fields to sources 
without causing breakage by APT. This can include comments, version information, 
and (as is the case with :ref:`repolib-module`, pretty, human-readable names. 

From the ``sources.list(5)`` manual page:

    This is a new format supported by apt itself since version 1.1. Previous 
    versions ignore such files with a notice message as described earlier. It is 
    intended to make this format gradually the default format, deprecating the 
    previously described one-line-style format, as it is easier to create, 
    extend and modify for humans and machines alike especially if a lot of 
    sources and/or options are involved.

.. _deb822-technical:

===================================
DEB822 Source Format Specifications
===================================

Following is a description of each field in the deb822 source format.


.. _deb822-field-enabled:

Enabled:
========

Enabled: (value: "yes" or "no", required: No, default: "yes")
    Tells APT whether the source is enabled or not. Disabled sources are not 
    queried for package lists, effectively removing them from the system 
    sources while still allowing reference or re-enabling at any time. 

.. _deb822-field-types:

Types:
======

Types: (value: "deb" or "deb-src", required: Yes)
    Defines which types of packages to look for from a given source; either 
    binary: ``deb`` or source code: ``deb-src``. The ``deb`` type references a 
    typical two-level Debian archive providing packages containing pre-compiled 
    binary data intended for execution on user machines. The ``deb-src`` type 
    references a Debian distribution's source code in the same form as the ``deb``
    type. A ``deb-src`` line is required to fetch source pacakge indices. 


.. _deb822-field-uris:

URIs:
=====

URIs: (value: string(s), required: Yes)
    The URI must specify the base of the Debian distribution archive, from which 
    APT finds the information it needs. There must be a URI component present in 
    order for the source to be valid; multipls URIs can be configured 
    simultaneously by adding a space-separated list of URIs.

    A list of the current built-in URI Schemas supported by APT is available at
    the `Debian sources.list manpage <https://manpages.debian.org/stretch/apt/sources.list.5.en.html#URI_SPECIFICATION>`_.


.. _deb822-field-suites:

Suites:
=======

Suites: (value: strings(s), required: Yes)
    The Suite can specify an exact path in relation to the URI(s) provided, in 
    which case the :ref:`deb822-field-components` **must** be omitted and suite 
    **must** end with a slash ( ``/`` ). Alternatively, it may take the form of 
    a distribution version (e.g. a version codename like ``disco`` or ``artful``
    ). If the suite does not specify a path, at least one 
    :ref:`deb822-field-component` **must** be present.


.. _deb822-field-components:

Components: 
===========

Components: (value: string(s), required: see :ref:`deb822-field-suites`)
    Components specify different sections of one distribution version present in 
    a Suite. If :ref:`deb822-field-suites` specifies an exact path, then no 
    Components may be specified. Otherwise, a component **must** be present.


.. _deb822-options:

Options
=======

Sources may specify a number of options. These options and their values will 
generally narrow a set of software to be available from the source or in some 
other way control what software is downloaded from it. An exhaustive list of 
options can be found at the
`Debian sources.list manpage <https://manpages.debian.org/stretch/apt/sources.list.5.en.html#THE_DEB_AND_DEB-SRC_TYPES:_OPTIONS>`_.


.. _deb822-fields-repolib:

RepoLib-Specific Deb822 Fields
==============================

RepoLib presently defines a single internal-use fields which it adds to deb822 
sources that it modifies. 

X-Repolib-Name:
---------------

X-Repolib-Name: (value: string, required: no, default: filename)
    This field defines a formatted name for the source which is suitable for 
    inclusion within a graphical UI or other interface which presents source 
    information to an end-user. As a :ref:`repolib-module` specific field, this 
    is silently ignored by APT and other tools operating with deb822 sources and 
    is only intended to be utilized by :ref:`repolib-module` itself.


.. _deb822-examples:

========
Examples
========

The following specifies a binary and source-code source fetching from the 
primary Ubuntu archive with multiple suites for updates as well as several components::

    Enabled: yes
    Types: deb deb-src
    URIs: http://archive.ubuntu.com/ubuntu
    Suites: disco disco-updates disco-security disco-backports
    Components: main universe multiverse restricted

This is a source for fetching Google's Chrome browser, which specifies a CPU 
architecture option and a RepoLib Name::

    X-Repolib-Name: Google Chrome 
    Enabled: yes
    URIs: http://dl.google.com/linux/chrome/deb
    Suites: stable
    Components: main
    Architectures: amd64

This specifies a source for downloading packages for System76's Pop!_OS::

    X-Repolib-Name: Pop!_OS PPA
    Enabled: yes
    Types: deb
    URIs: http://ppa.launchpad.net/system76/pop/ubuntu
    Suites: disco
    Components: main

Following is a PPA source which has been disabled::

    X-Repolib-Name: ZNC Stable
    Enabled: no
    Types: deb
    URIs: http://ppa.launchpad.net/teward/znc/ubuntu
    Suites: disco
    Components: main
