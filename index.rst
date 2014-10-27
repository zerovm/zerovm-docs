.. _index:

Welcome to ZeroVM's Documentation!
==================================

:ref:`ZeroVM <zerovm>` is a lightweight virtualization technology based on
`Google Native Client (NaCl) <http://en.wikipedia.org/wiki/Google_Native_Client>`_.
It is a sandbox which isolates and runs a single process at a time,
unlike other virtualization and container technology which provide an entire
virtualized operating system and execution environment capable of running
multiple processes.

:ref:`ZeroCloud <zerocloud>` is a platform based on ZeroVM and
`Openstack Swift <http://swift.openstack.org>`_ which can be used to run all
sorts of applications, including
`REST <http://en.wikipedia.org/wiki/Representational_state_transfer>`_
services, `MapReduce <http://en.wikipedia.org/wiki/MapReduce>`_, and batch
processing of any kind. Applications which deal with a lot of data or require
significant parallel processing are a good fit for ZeroCloud.


Where should I start?
---------------------

If you're interested in learning in depth about the core ZeroVM sandbox
technology, check out the :ref:`ZeroVM core documentation <zerovm>`.

If you're interested in developing web applications, MapReduce applications, or
just to need handle large amounts of data, you don't need to know too many
details about the core ZeroVM sandbox technology; you can skip straight to the
:ref:`ZeroCloud section<zerocloud>`.


.. _zerovm:

ZeroVM: Lightweight, single process sandbox
-------------------------------------------

.. toctree::
   :maxdepth: 2
   :numbered:

   zerovm/overview
   zerovm/isolation_security
   zerovm/filesystem
   zerovm/channels_io
   zerovm/manifest
   zerovm/embed

.. _zerocloud:

ZeroCloud: Cloud storage & compute platform
-------------------------------------------

.. toctree::
   :maxdepth: 2
   :numbered:

   zerocloud/overview
   zerocloud/devenv
   zerocloud/runningcode
   zerocloud/snakebin/snakebin


ZeroVM Command Line Tools
-------------------------

Here are some tools which help with developing, testing, bundling, and
deploying ZeroVM/ZeroCloud applications:

.. toctree::

   clitools


Contributing to ZeroVM
----------------------

.. toctree::
   :maxdepth: 2

   contributing
   contact


Further Reading
---------------

.. toctree::

   glossary

