.. _applications:

Applications on Zebra
=============================


Simple applications
-------------------

Examples of single applications would be as follows:

#. watermark a digital photograph
#. scale photographs or other artefacts for various display form factors
#. grep log files
#. calculate hash sums of storage objects

The examples above are all single stage applications i.e. they operate on storage objects and may either result in new objects (examples 1, 2 and 4) or output that is sent back to the client (example 3).


Multi-stage applications
------------------------

ZeroVM instances may also be wired up so that the respective applications operate in `map/reduce style <https://en.wikipedia.org/wiki/Mapreduce>`_.

Examples of this application style would be:

#. document indexing
#. distributed pattern-based searching
#. distributed sorting

Please note also that the ZeroVM team maintains a `map/reduce library <https://github.com/zerovm/zrt/tree/master/lib/mapreduce/doc>`_ to facilitate the construction of such applications.


Deploying Applications on Zebra
-------------------------------

ZeroVM applications are best prepared and deployed using the `ZeroVM Package Manager </projects/zerovm-zpm/>`_. See `this section </projects/zerovm-zpm/en/latest/intro.html#creating-a-zerovm-application>`_ for a simple example.

