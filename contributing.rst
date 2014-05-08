
Contributing to ZeroVM
======================

We love contributors!

Pull Requests
-------------

Please use GitHub pull requests when contributing code. We will try to
quickly review and merge your code. Feel free to remind us on IRC or
the mailinglist if it takes more than a couple of days for us to
respond to a pull request.

Rebasing
""""""""

You should make sure to rebase your code to the head of ``master``
before submitting the pull request. That ensures that there will be no
merge conflicts initially.

If the pull request is not merged quickly, it can become outdated.
This happens when other pull requests are merge in front of it and
cause merge conflicts with the code you changed. You should then
rebase the code again.

You rebase your pull request with::

   $ git checkout master
   $ git pull upstream master
   $ git rebase master your-branch

This will first make sure that your ``master`` is up to date with
regards to the upstream repository. The upstream should be the
repository you forked on GitHub (the repository living under
``github.com/zerovm/``).

It will generally be appreciated if you keep your code up to date in
this way -- even when there are no conflicts. Rebasing regularly
simplifies the history.


Contribution Guidelines
-----------------------

We follow the C4_ contribution guidelines.

Coding Style
""""""""""""

For Python-based projects, we enforce PEP8_ and Pyflakes_ standards. Checks are
run automatically on each pull request to signal if there is a style violation.


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
``master`` into ``stable``. It looks like this::

   master: ----- o --- o --- o --- o
                /           /       \
   stable: --- o --------- o ------- o

This merge brings all the new features developed since the last
release onto the ``stable`` branch.

.. _c4: https://github.com/zerovm/zvm-community/blob/master/process/c4_1.md
.. _flake8: http://flake8.readthedocs.org/
.. _pep8: http://legacy.python.org/dev/peps/pep-0008/
.. _pyflakes: https://launchpad.net/pyflakes
.. _git: https://www.kernel.org/pub/software/scm/git/docs/gitworkflows.html
