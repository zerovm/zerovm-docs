.. _zerocloud-pythonapps:

Developing Python applications
==============================

In the section :ref:`Running code on ZeroCloud <running-code>` we saw some
examples of running basic Python programs. This tutorial will cover Python
application development in more depth, including more detailed descriptions
of the directives in the application template (``zapp.yaml``). It will also
cover how to include third party Python libraries in your zapp.

.. _zerocloud-pythonapps-template:

Python application template
---------------------------

The most covenient way to build Python applications on ZeroCloud is use to
utilities build into the ``zpm`` tool.

To create a new application, simply run:

.. code-block:: bash

    $ zpm new --template python
    Created './zapp.yaml'
    Created './.zapp'
    Created './.zapp/tox.ini'

Notice that this creates a couple of files and a directory. ``zapp.yaml`` is
this application template, and most of time you'll be modifying this file to
make changes to your application config. ``.zapp/`` is "hidden" directory which
contains extra artifacts to assist with bundling your application, including
``tox.ini`` which is used to download and cache third-party (pure) Python
dependencies. For the most part, you will not need to directly change anything
in the ``.zapp/`` directory, although some corner cases <link> require this.

The default ``zapp.yaml`` should look something like this:

.. literalinclude:: python-zapp.yaml
   :language: yaml

Let's look at each section in a bit more detail:

.. literalinclude:: python-zapp.yaml
   :language: yaml
   :lines: 1-3

The ``project_type`` directive simply indicates that this is a Python project.
This is so ``zpm`` understands what to do exactly for things like application
bundling, which are specific to the project type.

.. literalinclude:: python-zapp.yaml
   :language: yaml
   :lines: 5-27

The ``execution`` section can contain one or more ``groups``. We call
them "groups" because certain configurations can result in the creation of many
ZeroVM instances, as is the case with
:ref:`MapReduce applications on ZeroCloud <runningcode-mapreduce>`. Each
group must define a ``name`` which is unique among all of the groups.

``path`` defines the base image to use for execution. The format of this field
is as follows: ``file://<image-name>:<exe-name>``
In this example, we indicate that the ``python2.7`` base image shall be used,
and from that, we execute the ``python`` binary contained within that image.

``args`` is used to supply additional arguments to the ``python`` executable.
In most cases, we will simply invoke a Python script by settings args to
something like ``foo.py``, but you can supply additional positional arguments
as well, just as if you were running a Python script from a command line
(``python foo.py arg1 arg1 etc.``).

``devices`` defines which I/O devices are to be made available to the ZeroVM
instances in this group, and how the devices should be configured. See
:ref:`I/O Devices <zerocloud-devices>` for more detail.

.. TODO(larsbutler): Document the default devices: stdin, stdout, image, script, etc.

.. literalinclude:: python-zapp.yaml
   :language: yaml
   :lines: 29-34

The ``meta`` section simply contains metadata about the application, and should
be pretty self-explanatory. The only required property here is ``name``, which
is used to contstruct the ``.zapp`` file when ``zpm bundle`` is called. For
example, if the ``name`` is ``foo``, then ``zpm bundle`` will bundle the
application as ``foo.zapp``.

.. literalinclude:: python-zapp.yaml
   :language: yaml
   :lines: 36-43

The ``help`` section is deprecated. You can ignore it for now.

.. literalinclude:: python-zapp.yaml
   :language: yaml
   :lines: 45-47

The ``bundling`` section defines which files/directories within the project
directory should be included in the zapp at bundle time. You can include
individual files in this way, or entire directories.

.. _zerocloud-pythonapps-3rd-party-deps:

Including third party (pure) Python dependencies
------------------------------------------------

``zapp.yaml`` has an optional directive called ``dependencies``. In this
section you can list third party Python dependencies, which will be fetched
from `PyPI <https://pypi.python.org/pypi>`_. Note that third party Python code
must be *pure* Python. Here are a few examples:

.. code-block:: yaml

    dependencies: [
        "pngcanvas",
    ]

In this example, we declare the `pngcanvas library
<https://pypi.python.org/pypi/pngcanvas/>`_ as a dependency. This is the
simplest and most typical example.

Here is a more complicated example:

.. code-block:: yaml

    dependencies: [
        "pngcanvas",
        ["glibc", "glibc", "pyglibc"],
        ["purepng", "png"],
    ]

In this example, we declare
`pngcanvas <https://pypi.python.org/pypi/pngcanvas>`_,
`glibc <https://pypi.python.org/pypi/glibc>`_, and
`purepng <https://pypi.python.org/pypi/purepng>`_ as dependencies.

Because ``glibc`` installs both a ``glibc.py`` module and a ``pyglibc``
package, we specify both of those in the tail of the list.

Similarly, we also want to include
`purepng <https://pypi.python.org/pypi/purepng>`_. The difference here is that
while the package name on PyPI is ``purepng``, the only Python module installed
is simply called ``png``.

If you don't know which modules/packages to include from a given Python
package, you can either look at the ``setup.py`` (a ``glibc`` example:
https://github.com/zyga/python-glibc/blob/1097a1e5d1e243f08a4872fdb0f088c3c019bc12/setup.py#L35-36)
or have a look at the ``.zapp/.zapp/venv/lib/python2.7/site-packages``
directory after you run ``zpm bundle`` (which will install and cache the
dependencies you specify). This may take some trial and error and multiple
``zpm bundle --refresh-deps`` commands (see
:ref:`below <zerocloud-pythonapps-refresh-deps>`). Fortunately, you won't need
to do this often.

.. note::

    The dependency management feature of ``zpm`` could be the target of future
    improvement. The initial implementation works for a lot of cases, but may
    be inefficient for more complex corner cases and varied Python packaging
    configurations. If you run into a case which doesn't work, or otherwise
    have problems with or questions about this feature, please `file a bug
    report <https://github.com/zerovm/zpm/issues>`_.

..

.. _zerocloud-pythonapps-refresh-deps:

Refreshing dependencies
+++++++++++++++++++++++

Dependencies are cached in the ``.zapp/`` directory so that ``zpm`` doesn't
redundantly re-fetch dependencies each time you call ``zpm bundle``. However,
at times you will need to add/remove dependencies, and therefore refresh the
cached Python packages. To do this, you can simply run:

.. code-block:: bash

    $ zpm bundle --refresh-deps

This will clear the cache, re-fetch all dependencies per the ``depends``
directive in the ``zapp.yaml``, and bundle your zapp as usual.

.. tip::

    To double-check if a change in dependencies is reflected correctly in your
    zapp, you can use ``tar tf <myapp>.zapp`` to check the contents of the
    archive.

Exceptional cases
+++++++++++++++++

Some Python packages on PyPI may specify an external download location.
The `BitVector library <https://pypi.python.org/pypi/BitVector>`_ is one such
example. This can cause problems when ``zpm bundle`` is called. Here is an
excerpt of one such error:

.. code-block:: text
   :emphasize-lines: 3

    Downloading/unpacking BitVector (from -r /home/user1/projects/foo/.zapp/deps.txt (line 1))
      Could not find any downloads that satisfy the requirement BitVector (from -r /home/user1/projects/foo/.zapp/deps.txt (line 1))
      Some externally hosted files were ignored (use --allow-external BitVector to allow).

To workaround this, modify your ``.zapp/tox.ini`` and add a custom
``install_command`` to the ``[testenv:venv]`` section:

.. code-block:: ini
   :emphasize-lines: 8-10

    [tox]
    toxworkdir={toxinidir}/.zapp
    envlist = venv
    skipsdist = true

    [testenv:venv]
    deps = -r{toxinidir}/deps.txt
    install_command = pip install
                      --allow-external BitVector
                      {opts} {packages}

Similar errors can occur if the external source is unverified, which can result
in errors like the following. (Indeed, adding the
``--allow-external BitVector`` is not enough to successfully install this
specific dependency.)

.. code-block:: text
   :emphasize-lines: 3

    Downloading/unpacking BitVector (from -r /home/user1/projects/foo/.zapp/deps.txt (line 1))
      Could not find any downloads that satisfy the requirement BitVector (from -r /home/user1/projects/foo/.zapp/deps.txt (line 1))
      Some insecure and unverifiable files were ignored (use --allow-unverified BitVector to allow).

In this case, the final step for this workaround is to further edit the
``.zapp/tox.ini`` and adding the suggested ``--allow-unverified`` option to the
``pip install`` command:

.. code-block:: ini
   :emphasize-lines: 10

    [tox]
    toxworkdir={toxinidir}/.zapp
    envlist = venv
    skipsdist = true

    [testenv:venv]
    deps = -r{toxinidir}/deps.txt
    install_command = pip install
                      --allow-external BitVector
                      --allow-unverified BitVector
                      {opts} {packages}

After making these changes, run ``zpm bundle -r`` and everything should work
correctly.
