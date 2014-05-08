
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

Ordering Commits
""""""""""""""""

Your commits should tell a story to the reviewer. You should therefore
make sure to order them so they can be read like that. This means that
you should:

* Begin with the easy and non-controversial changes first. Consider
  putting these changes into their own pull request so you can get
  them out of the way.

* Make sure each commit depends on the past only, not the future. It
  is very confusing for a reviewer to read commit A if it calls a
  function introduced later in commit B or C.

Modern distributed version control systems like Git gives you the
tools to fix these mistakes when they occur. Using the interactive
mode of ``git rebase``, you can easily reorder commits. While having
your feature branch checked out, you run::

   $ git rebase -i master

This will open your editor with a file that shown an "execution plan"
for the interactive rebase. Each line represents a commit and by
reordering the lines you instruct Git to reorder the corresponding
commits.

After you save the file and close the editor, Git will begin
reordering commits. If conflicts occur, you should use ``git
mergetool`` to solve them. This starts your three-way merge tool which
should let you figure out how to best solve the conflicts.


Fixing Your Own Mistakes
""""""""""""""""""""""""

Nobody writes perfect code in the first try, so it often happens that
you discover a mistake in an earlier commit. Please pay attention to
this situation. When a reviewer sees a bug or some bad design in
commit A, he will likely stop and begin write a comment about it. Even
if you fix the problem yourself in commit B or C, it would have been
much more helpful if you had avoided introducing it at all.

If the fix concerns the last commit you made, then simply use ``git
commit --amend`` to redo the commit. You can use ``git commit
--amend`` as many times you want to fine-tune a commit.

If you want to fix something that committed further in the past, you
should instead follow this procedure:

1. Commit the fix by itself. Use ``git add -p`` to stage just the fix
   by itself if there are other changes in the same file.

2. Use ``git rebase -i`` to reorder the commits so that the bugfix is
   right after the commit that introduced the bug. In addition to
   reordering the commits, change the action from ``pick`` to
   ``fixup``.

This will do the same as if you had used ``git commit --amend`` to fix
the bug. With these steps, you can easily fix past mistakes.


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
