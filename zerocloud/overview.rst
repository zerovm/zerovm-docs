.. _zerocloud-overview:

What is ZeroCloud?
==================

ZeroCloud is a converged cloud storage and compute platform, powered by
`OpenStack Swift <http://swift.openstack.org>`_ and
`ZeroVM <https://github.com/zerovm/zerovm>`_. It combines the massively
scalable object storage capabilities of Swift with the application isolation
of ZeroVM to create a platform for developing cloud applications.

Use cases
---------

Not all types of applications are suitable for the ZeroCloud platform. The
only real data persistence mechanism available is OpenStack Swift object
storage, which is
`eventually consistent <http://en.wikipedia.org/wiki/Eventual_consistency>`_.
This makes ZeroCloud most suitable for highly-available and partition-tolerant
applications which process a lot of data.

Here are some types of applications which are a good match for ZeroCloud:

- MapReduce (searching, sorting, analytics, etc.)
- Batch processing (logs, images, etc.)
- File server/repository applications

ZeroCloud also provides tools for easily building REST services for your
applications.

Language support
----------------

Currently, you can only write applications for ZeroCloud using Python and
C/C++. This limitation comes from the ZeroVM execution environment, which
requires applications to be cross-compiled to
`NaCl <http://en.wikipedia.org/wiki/Google_Native_Client>`_ for validation
and execution.

The recommended development language for ZeroCloud is Python. Python 2.7.3
has been ported to NaCl and is available to use on ZeroVM and ZeroCloud.
See https://github.com/zerovm/zpython2.
