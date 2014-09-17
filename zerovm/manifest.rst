.. _zerovm-manifest:

ZeroVM Manifest
===============

A manifest file is the most primitive piece of input which must be
provided to ZeroVM. Here is an example manifest:

.. code-block:: text

    Version = 20130611
    Timeout = 50
    Memory = 4294967296,0
    Program = /home/me/myapp.nexe
    Channel = /dev/stdin,/dev/stdin,0,0,8192,8192,0,0
    Channel = /dev/stdout,/dev/stdout,0,0,0,0,8192,8192
    Channel = /dev/stderr,/dev/stderr,0,0,0,0,8192,8192
    Channel = /home/me/python.tar,/dev/1.python.tar,3,0,8192,8192,8192,8192
    Channel = /home/me/nvram.1,/dev/nvram,3,0,8192,8192,8192,8192

The file consists of basic ZeroVM runtime configurations and one or more
:ref:`channels <zerovm-channels-io>`.

Required attributes:

* ``Version``: The manifest format version.
* ``Timeout``: Maximum life time for a ZeroVM instance (in seconds). If
  a user program (untrusted code) exceeds the time limit, the ZeroVM
  executable will return an error.
* ``Memory``: Contains two 32-bit integer values, separated by a comma. The
  first value specifies the amount of memory (in bytes) available for the user
  program, with a maximum of 4294967296 bytes (4 GiB). The second value
  (0 for disable, 1 for enable) sets memory entity tagging. FIXME: This etag
  feature is undocumented.
* ``Program``: Path to the untrusted executable (cross-compiled to NaCl)
  on the host file system.

.. TODO(larsbutler): document `Node`, `Nameserver`, and `Job`.

.. _zerovm-manifest-channel-max:

Channel Definition Limit
------------------------

A manifest can define a maximum of 10915 channels.
