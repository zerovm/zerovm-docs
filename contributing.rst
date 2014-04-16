
Contributing to ZeroVM
======================

We love contributors!


Using GitHub Pull Requests
--------------------------

Please use GitHub pull requests when contributing code.


Contribution Guidelines
-----------------------

We follow the C4_ contribution guidelines.

Coding Style
""""""""""""

For Python-based projects, we follow flake8_ on the source. This means
that you should follow the style guides in PEP8_ closely. Jenkins will
inform you if there is a problem with your pull request.


Branches
--------

We follow a workflow similar to Git_ where we maintain a branch called
``stable`` for bugfix releases. This branch is continiously merged
into ``master`` during normal development -- this ensures that
bugfixes are incorporated with the newest features.

As ASCII art it looks like this::

   master: ----- o --- o --- o --- o
                /           /
   stable: --- o --------- o

All releases are made from the ``stable`` branch. We :ref:`release
bugfixes <bugfix-releases>` once per month by tagging and releasing
whatever code we have in the ``stable`` branch. We make a
:ref:`feature release <feature-releases>` every three months. These
are also made from ``stable``, but the are preceded by a merge of
``master`` into ``stable. It looks like this::

   master: ----- o --- o --- o --- o
                /           /       \
   stable: --- o --------- o ------- o

This merge brings all the new features developed since the last
release onto the ``stable`` branch.

.. _c4: https://github.com/zerovm/zvm-community/blob/master/process/c4_1.md
.. _flake8: http://flake8.readthedocs.org/
.. _pep8: http://legacy.python.org/dev/peps/pep-0008/
.. _git: https://www.kernel.org/pub/software/scm/git/docs/gitworkflows.html
