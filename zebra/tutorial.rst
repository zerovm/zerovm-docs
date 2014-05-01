Tutorial
========

This guide will help get you started using the
`Zebra playground <https://zebra.zerovm.org>`_. Included are guides on
getting account access to Zebra, installing command-line tools, and configuring
your `zapp <todo link>`_ development environment.

There are also some sample applications writing guides to demonstrate how
ZeroVM applications are structured and what they can do.

#. :ref:`zebra-get-access`
#. :ref:`zebra-install-cli-tools`
#. :ref:`zebra-config-devenv`
#. :ref:`zebra-sample-apps`

.. _zebra-get-access:

Getting access
--------------

.. _zebra-install-cli-tools:

Installing command-line tools
-----------------------------

To run ZeroVM applications on Zebra/ZeroCloud, you will at least need to
install the `ZeroVM Package Manager </projects/zerovm-zpm>`_. ``zpm`` is
written in pure Python and should run on all major platforms (Linux, OSX,
Windows, etc.).

Installing ``zpm`` directly from `GitHub <https://github.com/zerovm/zpm>`_::

    $ pip install git+https://github.com/zerovm/zpm.git

If you want to test your application locally before deploying it you will need
to install ZeroVM itself, as well a few other command-line utilities. At
present, the only officially supported platform for installing these tools is
`Ubuntu 12.04 LTS <http://releases.ubuntu.com/12.04/>`_.

Installing ZeroVM and other command-line tools (from the latest packages)::

    $ sudo apt-get install python-software-properties
    $ sudo add-apt-repository ppa:zerovm-ci/zerovm-latest
    $ sudo apt-get update
    $ sudo apt-get install zerovm-cli

To locally run Python applications on ZeroVM, you will also need the
cross-compiled `NaCL` Python distribution tarball copied to a well-known location on
your local disk (in your user home directory, for example). ZeroVM will need to
mount and use this as a file system image.

At present, a Python2.7-based distribution is available::

    $ cd ~
    $ wget http://packages.zerovm.org/zerovm-samples/python.tar

.. _zebra-config-devenv:

Configuring your development environment
----------------------------------------

``zpm`` must authenticate to Zebra/ZeroCloud to deploy applications. See
`configuring zpm auth for ZeroCloud
</projects/zerovm-zpm/zerocloud-auth-config>`_.

.. _zebra-sample-apps:

Sample applications
-------------------

To try out the sample applications create a working directory to store your
project files. For example::

    $ mkdir ~/zebra
    $ cd ~/zebra

Each sample application below includes complete source code. Each one is
progressively more complex than the next. For best results, it is recommended
to try them out in order.

#. :ref:`zebra-hello-world-sample`
#. :ref:`zebra-system-info-sample`
#. :ref:`zebra-wordcount-sample`
#. :ref:`zebra-parallel-wordcount-sample`

.. _zebra-hello-world-sample:

Hello, World!
"""""""""""""

This application is a classic "Hello, World!" application to test that all of
the ZeroVM components are working correctly.

1. Create the project directory
...............................

.. code-block:: bash

    $ mkdir ~/zebra/hello
    $ cd ~/zebra/hello

2. Add code
...........

Create a ``hello.py`` file in the current directory and a simple print
statement. For example:

.. code-block:: python

    print('Hello, ZeroVM!')

3. Create a template zapp config file (``zapp.yaml``)
....................................................................

``zpm`` can create this file for you:

.. code-block:: bash

    $ zpm new

4. Customize the zapp config file
.................................

For now, we only need to edit two things: the execution group name and the
bundling list.

Change

.. code-block:: yaml

    execution:
      groups:
        - name: ""

to

.. code-block:: yaml

    execution:
      groups:
        - name: "hello"

Then change

.. code-block:: yaml

    bundling:
        - ""

to

.. code-block:: yaml

    bundling:
        - "hello.py"

The final result should look something like this:

.. code-block:: yaml

    # This section describes the runtime behavior of your zapp: which
    # groups of nodes to create and which nexe to invoke for each.
    execution:

      # Your application can consist of multiple groups. This is typically
      # used for map-reduce style jobs. This is a list of groups, so
      # remember to add "-" infront of each group name.
      groups:

          # Name of this group. This is used if you need to connect groups
          # with each other.
        - name: "hello"

          # The NaCl executable (nexe) to run on the nodes in this group.
          path: file://python2.7:python

          # Command line arguments for the nexe.
          args: ""

          # Input and output devices for this group.
          devices:
          - name: python2.7
          - name: stdout

    # Meta-information about your zapp.
    meta:
      Version: ""
      name: "hello"
      Author-email: ""
      Summary: ""

    help:
      # Short description of your zapp. This is used for auto-generated
      # help.
      description: ""

      # Help for the command line arguments. Each entry is a two-tuple
      # with an option name and an option help text.
      args:
      - ["", ""]

    # Files to include in your zapp. Your can use glob patterns here, they
    # will be resolved relative to the location of this file.
    bundling:
      - "hello.py"

Check the `zpm documentation
</projects/zerovm-zpm>`_ for more information about the ``zapp.yaml`` contents.

5. Test the application locally using ``zvsh``
..............................................

.. note::

    To run ``zvsh`` you will need to install the ``zerovm-cli`` tools and the
    `NaCl` Python distribution. See :ref:`zebra-install-cli-tools`.

.. code-block:: bash

    $ zvsh --zvm-image ~/python.tar python @hello.py

6. Test the application on ZeroCloud/Zebra
..........................................

Now that we've tested the application on ZeroVM locally, it's time bundle it,
deploy it to ZeroCloud/Zebra, and test it there.

Bundling is simple. Just run the following command from your project root
directory:

.. code-block:: bash

    $ zpm bundle

This will create a ``hello.zapp`` file, which we can now deploy and execute. To
do so, we need to pick an existing Swift container as our deployment target.

.. tip::

    If a container doesn't exist, you can create it using the
    `python-swiftclient <https://github.com/openstack/python-swiftclient>`_
    with the ``swift post <container-name>`` command.

.. code-block:: bash

    $ zpm deploy hello.zapp mycontainer --execute

.. note::

    Omitting the ``--execute`` flag will only deploy the application. Work is
    under way to implement a separate ``zpm execute`` command. See
    https://github.com/zerovm/zpm/issues/37.


.. _zebra-system-info-sample:

System Info
"""""""""""

1. Create the project directory
...............................

2. Add code
...........

3. Create a template zapp config file (``zapp.yaml``)
.....................................................

4. Customize the zapp config file
.................................

5. Test the application locally using ``zvsh``
..............................................

6. Test the application on ZeroCloud/Zebra
..........................................


.. _zebra-wordcount-sample:

Word Count
""""""""""

1. Create the project directory
...............................

2. Add code
...........

3. Create a template zapp config file (``zapp.yaml``)
.....................................................

4. Customize the zapp config file
.................................

5. Test the application locally using ``zvsh``
..............................................

6. Test the application on ZeroCloud/Zebra
..........................................


.. _zebra-parallel-wordcount-sample:

Parallel Word Count
"""""""""""""""""""

1. Create the project directory
...............................

2. Add code
...........

3. Create a template zapp config file (``zapp.yaml``)
.....................................................

4. Customize the zapp config file
.................................

5. Test the application locally using ``zvsh``
..............................................

6. Test the application on ZeroCloud/Zebra
..........................................


