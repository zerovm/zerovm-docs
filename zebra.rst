.. _zebra-docs:

**************************************************
Zebra
**************************************************


Introduction
==================================================

Zebra is an `OpenStack Swift <https://wiki.openstack.org/wiki/Swift>`_ cloud storage container that is `ZeroVM <http://zerovm.org/>`_-enabled i.e. it is capable of running ZeroVM applications in addition to performing static storage operations.

How is this interesting and what can you do with it? In a nutshell, you can deploy and run applications that operate on cloud data directly, safely and with a high degree of parallelism.

ZeroVM applications are usually written in `Python <https://www.python.org/>`_. In the Zebra context we run a separate, one-off ZeroVM instance for each storage datum. These instances execute the configured/desired application on a single storage datum and are disposed of afterwards.


Simple applications
==================================================

Examples of single applications would be as follows:

#. watermark a digital photograph
#. scale photographs or other artefacts for various display form factors
#. grep log files
#. calculate hash sums for storage objects

These examples above are all single stage applications i.e. they operate on storage objects and may either result in new objects (examples 1, 2 and 4) or output that is sent back to the client (example 3).



Multi-stage applications
==================================================

ZeroVM instances may also be wired up so that the respective applications operate in `map/reduce style <https://en.wikipedia.org/wiki/Mapreduce>`_.

Examples of this application style would be:

#. document indexing
#. distributed pattern-based searching
#. distributed sorting

Please note also that the ZeroVM team maintains a `map/reduce library <https://github.com/zerovm/zrt/tree/master/lib/mapreduce/doc>`_ to facilitate the construction of such applications.

Tutorial
==================================================



How do I gain access to Zebra?
--------------------------------------------------



How do I prepare and deploy ZeroVM application?
--------------------------------------------------
