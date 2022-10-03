.. _key_object:

==========
Key object
==========

The SourceKey object is the representation for signing keys used to validate 
software packages downloaded from repositories. 


Attributes
==========

.. _key-path

path
----

SourceKey.path
    A :obj:`Pathlib.Path` object pointing to this key's file location on disk. 

.. _key-gpg

gpg
---

SourceKey.gpg
    A :obj:`gnupg.GPG` object used for importing and manipulating GPG data.

.. _key-data

data
----

SourceKey.data
    The binary data stored in this key, used to verify package signatures.


Methods
=======

.. _key-reset_path

reset_path()
------------

SourceKey.reset_path(name:str='', path:str='', suffix:str='archive-keyring') -> None
    (Re)sets the path object for this key to the key file specified. If a ``name``
    is given, then the file is expected to be located within the system default
    signing key directory ``/etc/apt/keyrings``. If a ``path`` is spefified, 
    then it is assumed to be the full path to the keyring file on disk.

name
^^^^
The name of a keyring file located within the system signing key directory, less
any suffix or file extensions.

path
^^^^
The absolute path to a keyring file located at any readable location on disk.

suffix
^^^^^^
A suffix to append to the file name before the file extension. (Default:
``'archive-keyring'``)

.. _key-setup_gpg

setup_gpg()
-----------

SourceKey.setup_gpg() -> None
    Sets up the :ref:`key-gpg` object for this key and loads key data from disk
    (if present).

.. _key-save_gpg

save_gpg()
----------

SourceKey.save_gpg() -> None
    Saves the GPG key data to disk.

.. _key-delete_key

delete_key()
------------

SourceKey.delete_key() -> None
    Deletes the key file from disk.

.. _key-load_key_data

load_key_data()
---------------

SourceKey.load_key_data(raw=|ascii=|url=|fingerprint=) -> None
    Fetches and loads a key from some remote source. Keys can be loaded from one
    of:
        * Raw internal data (:obj:`bytes`)
        * ASCII-armored keys (:obj:`str`)
        * Internet URL download (:obj:`str`)
        * Public GPG Keyserver Fingerprint (:obj:`str`)

raw=data (:obj:`bytes`)
^^^^^^^^^^^^^^^^^^^^^^^
Load a key from raw binary data. This is ideal when importing a key which has 
already been loaded from a binary data file or stream.

ascii=armor (:obj:`str`)
^^^^^^^^^^^^^^^^^^^^^^^^
Load a key from an ASCII-Armored string. 

url=url (:obj:`str`)
^^^^^^^^^^^^^^^^^^^^
Download a key over an HTTPS connection. Note that keys should only be downloaded
from secure sources.

fingerprint=fingerprint (:obj:`str`)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Fetch the key specified by ``fingerprint`` from a public keyserver.
