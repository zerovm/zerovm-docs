.. _zerovm-channels-io:

Channels and I/O
================

All I/O in ZeroVM is modeled through an abstraction called "channels".
Channels act as the communication medium between the host operating system
and a ZeroVM instance. On the host side, the channel can be pretty much
anything: a file, a pipe, a character device, or a TCP socket. Inside a ZeroVM
instance, the all channels look like files.

Channels Restrictions
---------------------

The most important thing to know about channels is that they must be declared
prior to starting a ZeroVM instance. This is no accident, and it bears
important security implications. For example: It would be impossible for user
code (which is considered to be "untrusted") to open and write to a socket,
*unless* the socket is declared beforehand. The same goes for files stored on
the host; there is no way to read from or write to host files unless the file
channels are declared in advance.

Channels also have several attributes to further control I/O behavior. Each
channel defintion must declare:

* number of read operations
* number of write operations
* total bytes limit for reads
* total bytes limit for writes

If channel limits are exceeded at runtime, the ZeroVM trusted code will raise
an ``EDQUOT`` (Quota exceeded) error.

Channels Definitions
--------------------

In addition to read/write limits, channel definitions consist of several other
attributes. Here is a complete list of channel attributes, including I/O
limits:

* ``uri``: Definition of a device on the host operating system. This can be
  a normal file, a TCP socket, a
  `pipe <http://en.wikipedia.org/wiki/Unix_file_types#Named_pipe>`_,
  or a
  `character device <http://en.wikipedia.org/wiki/Device_file#Character_devices>`_.

  For files, pipes, and character devices, the value of the ``uri`` is
  simply a file system path, e.g., ``/home/me/foo.txt``.

  TCP socket definitions have the following format: ``tcp:<host>:<port>``,
  where ``<host>>`` is an IP address or hostname and ``<port>`` is the TCP
  port.
* ``alias``: A file alias inside ZeroVM which maps to the device specified
  on the host by ``uri``. Regardless of the host type of the device,
  everything looks like a file inside a ZeroVM instance. That is, even a
  socket will appear as a file in the virtual in-memory file system, e.g,
  ``/dev/mysocket``. Aliases can have arbitrary definitions.
* ``type``: Choose from the following enumeration:
    - 0 (sequential read / sequential write)
    - 1 (random read / sequential write)
    - 2 (sequential read / random write)
    - 3 (random read / random write)
* ``etag``: Typically disabled (0). When enabled (1), record and report a
  checksum of all of the data which passed through the channel (both read
  and written.
* ``gets``: Limit on the number of read operations for this channel.
* ``get_size``: Limit on the total number of bytes which can be read from
  this channel.
* ``puts``: Limit on the number of write operations for this channel.
* ``put_size``: Limit on the total number of bytes which can be read from
  this channel.

Channels limits must be an integer value from 1 to 4294967296 (2^32).

If a :ref:`ZeroVM manifest file <zerovm-manifest>` (a plain-text file),
channels are defined using the following format:

.. code-block:: text

    Channel = <uri>,<alias>,<type>,<etag>,<gets>,<get_size>,<puts>,<put_size>

Here are some examples:

.. code-block:: text

    Channel = /home/me/python.tar,/dev/1.python.tar,3,0,4096,4096,4096,4096
    Channel = /dev/stdout,/dev/stdout,0,0,0,0,1024,1024
    Channel = /dev/stdin,/dev/stdin,0,0,1024,1024,0,0
    Channel = tcp:192.168.0.10:27175,/dev/myserver,3,0,65536,65536,65536,65536
