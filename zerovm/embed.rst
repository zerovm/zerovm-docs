.. _zerovm_embeddability:

Embeddability
=============

The lightweightness and security that ZeroVM provides makes it ideal for
embedding computation in virtually any existing system, particularly data
storage systems. You can embed "untrusted" computation in any system simply
by invoking ZeroVM as a subprocess, for example. Think
"`stored procedures <http://en.wikipedia.org/wiki/Stored_procedure>`_", but
much more powerful.

A prime example of this embeddability is :ref:`ZeroCloud <zerocloud-overview>`,
which facilitates data-local computation inside of
`OpenStack Swift <http://swift.openstack.org>`_.
