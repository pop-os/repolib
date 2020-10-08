.. _ppa-module-functions:

repolib.ppa Module functions
============================

The module containing the :ref:`ppa-source-object` class also contains two 
public helper functions that can be helpful in manual processing of the data for 
a :ref:`ppa-source-object`. 


.. _get-info-from-lp:

get_info_from_lp()
^^^^^^^^^^^^^^^^^^

repolib.ppa.get_info_from_lp(owner_name, ppa)
    Requests PPA information from Launchpad and returns a Dict containing the 
    JSON response. 

    * ``owner_name`` - The user or team name which hosts the PPA on launchpad.
    * ``ppa`` - The name of the ppa for which to fetch information. 

.. _add-key:

add_key()
^^^^^^^^^

repolib.ppa.add_key(fingerprint)
    Downloads the key with ``fingerprint`` from keyserver.ubuntu.com and adds it 
    to the system configuration. 

    * ``fingerprint`` - The fingerprint of the key to download and fetch. This 
      value is present in the JSON data returned by :ref:`get-info-from-lp`
      function.
