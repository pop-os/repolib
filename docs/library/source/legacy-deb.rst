.. _legacy-deb-object:

LegacyDebSource()
==============

class repolib.LegacyDebSource()
    A Source which is intended to contain multiple :ref:`deb-source-object` as
    a way to support traditional ``.list`` files with multiple deb lines. 

.. _legacy-source-sources:

``sources``
^^^^^^^^^^^

The ``sources`` attribute is a ``list`` which stores the different sub-sources 
of the :ref:`legacy-deb-objeect`. There is one source for each line of the
source file.

LegacyDebSource() methods
-------------------------

.. _legacy-make-names

make_names()
^^^^^^^^^^^^

LegacyDebSource.make_names()
    Creates a :ref:`ident` for this source based on the ident generated for the 
    first source in the :ref:`legacy-source-sources` attribute.

.. _legacy-load-from-sources:

load_from_sources()
^^^^^^^^^^^^^^^^^^^

LegacyDebSource.load_from_sources()
    Loads the source's attributes from the different sources in the 
    :ref:`legacy-source-sources` attribute. This allows :ref:`legacy-deb-object`
    to be manipulated like a normal :ref:`source-object`, with changes 
    propagating to the relevant source lines it contains.

.. _legacy-make-deblines

make_deblines()
^^^^^^^^^^^^^^^

LegacyDebSource.make_deblines()
    Returns a string with the final Deb-line output from the source.
