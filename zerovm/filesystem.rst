.. _zerovm-filesystem:

In-memory File System
=====================

A virtual in-memory file system is made available to ZeroVM by the ZeroVM
`RunTime environment (ZRT) <https://github.com/zerovm/zrt>`_. Writes which
occur at runtime are completely thrown away. The only way to persistently
write data is to map a file in the virtual file system to a file or other
device on the host operating system. This is accomplished by the use of
:ref:`channels <zerovm-channels-io>`.

Arbitrary file hierarchies can be loaded into a ZeroVM instance by mounting
tar archives as disk images. This is necessary particularly in the case of
the `ZeroVM Python interpreter port <http://github.com/zerovm/zpython>`_,
which requires not only a cross-compiled Python interpreter executable but
also the Python standard library packages and modules; these files must
accessible for Python programs to run inside ZeroVM. Any tarball can be
mounted to the virtual file system, and multiple images can be mounted
simultaneously. Each tarball is mounted by defining a channel, just as with
any other file. (Note that there is a `limit <zerovm-manifest-channel-max>` to
the number of channels per instance.)
