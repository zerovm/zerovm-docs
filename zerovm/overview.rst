.. _zerovm-overview:

ZeroVM Overview
===============

The primary function of ZeroVM is to isolate a single application and provide
a secure sandbox which cannot be broken out of. In other words, "untrusted"
code can run safely inside ZeroVM without breaking out and compromising the
host operating system. One can easily appreciate the utility of this by looking
at applications like the `Python.org shell <https://www.python.org/shell/>`_
and the `Go Playground <http://play.golang.org/>`_.

This comes with some necessary limitations. Run time, memory usage and I/O
must be carefully controlled to prevent abuse and resource contention among
processes.
