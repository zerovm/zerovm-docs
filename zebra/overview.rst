.. _overview:

Zebra Overview
==============


Introduction
------------

Zebra is an `OpenStack Swift <https://wiki.openstack.org/wiki/Swift>`_ cloud storage container that is `ZeroVM <http://zerovm.org/>`_-enabled i.e. it is capable of running ZeroVM applications in addition to performing static storage operations.

How is this interesting and what can you do with it? In a nutshell, you can deploy and run applications that operate on cloud data directly, safely and with a high degree of parallelism.

ZeroVM applications are usually written in `Python <https://www.python.org/>`_. In the Zebra context we run a separate, one-off ZeroVM instance for each storage datum. These instances execute the configured/desired application on a single storage datum and are disposed of afterwards.

