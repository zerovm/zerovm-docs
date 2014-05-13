Tutorial
========

This guide will help get you started using the
`Zebra playground <https://zebra.zerovm.org>`_. Included are guides on
getting account access to Zebra, installing command-line tools, and configuring
your `zapp <todo link>`_ development environment.

There are also some sample applications writing guides to demonstrate how
ZeroVM applications are structured and what they can do.

.. contents::
   :backlinks: none
   :depth: 1
   :local:

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

.. contents::
   :backlinks: none
   :depth: 1
   :local:

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
          args: ""

to

.. code-block:: yaml

    execution:
      groups:
        - name: "hello"
          args: "hello.py"

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
          path: file://python:python

          # Command line arguments for the nexe.
          args: "hello.py"

          # Input and output devices for this group.
          devices:
          - name: python
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

    $ zpm deploy mycontainer hello.zapp
    $ zpm execute mycontainer hello.zapp

.. tip::

    You can also deploy and execute a zapp using a single ``deploy`` command.
    For example:

    ``$ zpm deploy mycontainer hello.zapp --execute``


.. _zebra-system-info-sample:

System Info
"""""""""""

This application is meant to display information about the ZeroVM execution
environment. It is intended to show details like platform info, environment
variables, and filesystem details.

1. Create the project directory
...............................

.. code-block:: bash

    $ mkdir ~/zebra/sysinfo
    $ cd ~/zebra/sysinfo

2. Add code
...........

Create a ``sysinfo.py`` file in the current directory, and add the following
code:

.. code-block:: python

    import os
    import pprint
    import sys
    import time

    from datetime import datetime


    def hr():
        """
        Print a basic horizontal rule.
        """
        print('-' * 32)


    def platform():
        hr()
        print('sys.platform: %s' % sys.platform)
        print('os.name: %s' % os.name)
        print('os.uname(): %s' % str(os.uname()))


    def env():
        hr()
        print('Environment variables:')
        for k, v in os.environ.items():
            print '%s=%s' % (k, v)


    def numbers():
        hr()
        print('Numbers:')
        print(sys.long_info)
        print(sys.float_info)
        print('sys.maxint: %s' % sys.maxint)
        print('sys.maxsize: %s' % sys.maxsize)


    def syspath():
        hr()
        print('sys.path (for Python):')
        pprint.pprint(sys.path)


    def systime():
        hr()
        print('Current time: %s' % datetime.utcnow())
        try:
            print('CPU time: %s' % time.clock())
        except AttributeError:
            print('CPU time: Not available')


    def filesystem():
        hr()
        print('Contents of /:')
        for f in os.listdir('/'):
            print('/%s' % f)


    if __name__ == "__main__":
        platform()
        env()
        numbers()
        syspath()
        systime()
        filesystem()

3. Create a template zapp config file (``zapp.yaml``)
.....................................................

``zpm`` can create this file for you:

.. code-block:: bash

    $ zpm new

4. Customize the zapp config file
.................................

As with the :ref:`zebra-hello-world-sample` example, we only need to edit the
execution group name and the bundling list.

Change

.. code-block:: yaml

    execution:
      groups:
        - name: ""
          args: ""

to

.. code-block:: yaml

    execution:
      groups:
        - name: "sysinfo"
          args: "sysinfo.py"

Then change

.. code-block:: yaml

    bundling:
        - ""

to

.. code-block:: yaml

    bundling:
        - "sysinfo.py"

The final result should look something like this:

.. code-block:: yaml

    execution:

      groups:
        - name: "sysinfo"
          path: file://python:python
          args: "sysinfo.py"
          devices:
          - name: python
          - name: stdout

    meta:
      Version: ""
      name: "hello"
      Author-email: ""
      Summary: ""

    help:
      description: ""
      args:
      - ["", ""]

    bundling:
      - "sysinfo.py"


5. Test the application locally using ``zvsh``
..............................................

.. code-block:: bash

    $ zvsh --zvm-image ~/python.tar python @sysinfo.py

For contrast, try just running ``sysinfo.py`` on your host system and compare
the outputs:

.. code-block:: bash

    $ python sysinfo.py

6. Test the application on ZeroCloud/Zebra
..........................................

We can deploy and test ``sysinfo`` in a similar manner to
:ref:`zebra-hello-world-sample`.

.. code-block:: bash

    $ zpm bundle
    $ zpm deploy mycontainer sysinfo.zapp
    $ zpm execute mycontainer sysinfo.zapp


.. _zebra-wordcount-sample:

Word Count
""""""""""

This application is a single-process wordcount application which operates on a
single file. ``wordcount`` can be run directly on the host system or with
``zvsh`` to count the words in the single file. With ZeroCloud/Zebra, however,
we can configure the application to be run on multiple input files (without
modifying the code!).

1. Create the project directory
...............................

.. code-block:: bash

    $ mkdir ~/zebra/wordcount
    $ cd ~/zebra/wordcount

2. Add code
...........

Create a ``wordcount.py`` file in the current directory, and add the following
code:

.. code-block:: python

    import os
    import sys


    if __name__ == "__main__":
        if len(sys.argv) >= 2:
            # We can either get the input file name from the command-line:
            input_file = sys.argv[1]
            input_filename = input_file
        else:
            # Or we expect the input file to be mounted to /dev/input.
            # In this case, we expect the file to be stored in Swift.
            # Split off the swift prefix
            # Just show the container/file
            input_file = '/dev/input'
            input_filename = '/'.join(os.environ.get('PATH_INFO').split('/')[2:])

        total = 0

        with open(input_file) as fp:
            for line in fp:
                words = line.split()
                total += len(words)

        print('%s %s' % (total, input_filename))

3. Create a template zapp config file (``zapp.yaml``)
.....................................................

``zpm`` can create this file for you:

.. code-block:: bash

    $ zpm new

4. Customize the zapp config file
.................................

We will need to edit names and bundling parameters and add a mapping for the
input files. The final result should look something like this:

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
        - name: "wordcount"

          # The NaCl executable (nexe) to run on the nodes in this group.
          path: file://python:python

          # Command line arguments for the nexe.
          args: "wordcount.py"

          # Input and output devices for this group.
          devices:
          - name: python
          - name: stdout
          -
            name: input
            path: "swift://~/wordcount/text*.txt"

    # Meta-information about your zapp.
    meta:
      Version: ""
      name: "wordcount"
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
      - "wordcount.py"

5. Test input text
..................

To test ``wordcount``, we need some sample text. You can use any text files you
want (one or more). For convenience, a few small sample *Lorem ipsum* gibberish
files are provided below.

``text1.txt``::

    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut diam sapien,
    dictum eleifend erat in, luctus pellentesque est. Aliquam diam est,
    tincidunt ac bibendum non, vehicula ut enim. Sed vitae mi orci. Nam
    scelerisque diam ut orci iaculis dictum. Fusce consectetur consectetur
    risus ut porttitor. In accumsan mi ut velit venenatis tincidunt. Duis id
    dapibus velit, nec semper odio.  Quisque auctor massa vitae vulputate
    venenatis. Pellentesque velit eros, pretium in hendrerit a, viverra vitae
    neque. Vivamus mattis vehicula lectus vel fringilla. Curabitur sem urna,
    condimentum nec lectus non, tristique elementum sapien. Quisque luctus
    ultrices ante sed dignissim. Integer non commodo enim, quis semper diam.

``text2.txt``::

    Curabitur pulvinar diam eros, eget varius justo hendrerit sed. Maecenas
    hendrerit aliquam libero id mollis. Donec semper sapien tellus, sed
    elementum dolor ornare eu. Vestibulum lacinia mauris quis ipsum porta, ut
    lobortis sapien consectetur. Sed quis pretium justo, mattis aliquet nisl.
    Donec vitae elementum lectus. Morbi fringilla augue non elit pulvinar, non
    fermentum quam eleifend. Integer ac sodales lorem, a iaculis sapien.
    Phasellus vel sodales lorem. Integer consequat varius mi in pretium.
    Aliquam iaculis viverra vestibulum. Ut ut arcu sed orci malesuada pulvinar
    sit amet sed felis. Nullam eget laoreet urna. Sed eu dapibus quam. Nulla
    facilisi. Aenean non ornare lorem.

``text3.txt``::

    Vivamus lacinia tempor massa at molestie. Aenean non erat leo. Curabitur
    magna diam, ultrices quis eros quis, ornare vehicula turpis. Donec
    imperdiet et mi id vestibulum. Nullam tincidunt interdum tincidunt. Nullam
    eleifend vel mauris in bibendum. Maecenas molestie est ac rhoncus
    elementum. Duis imperdiet hendrerit congue. Quisque facilisis neque a
    semper egestas. Vestibulum nec lacus diam.  Nam vitae volutpat lacus.
    Donec sodales dui est, ac malesuada arcu sodales vitae.

6. Test the application locally
...............................

``wordcount`` can run on the host:

.. code-block:: bash

    $ python wordcount.py text1.txt

or it can be run in ZeroVM using ``zvsh``:

.. code-block:: bash

    $ zvsh --zvm-image ~/python.tar python @wordcount.py @text1.txt

7. Test the application on ZeroCloud/Zebra
..........................................

In the example test runs above, we were running ``wordcount`` only on a single
file. With the input file configuration we have made in ``zapp.yaml``, we can
submit a job to ZeroCloud and run multiple instances of ``wordcount`` on
multiple files, concurrently. The glob pattern we specified in the ``input``
device will instruct ZeroCloud to map one instance of ``wordcount`` to each
input file.

First, we need to upload our test files in the Swift object store. We can do
this using the ``python-swiftclient``. To start, create a new container for the
files:

.. code-block:: bash

    $ swift post wordcount

Now we can upload our input text files:

.. code-block:: bash

    $ swift upload wordcount text*.txt

Finally, we can bundle, deploy, and execute our ``wordcount`` application:

.. code-block:: bash

    $ zpm bundle
    $ zpm deploy wordcount wordcount.zapp
    $ zpm execute wordcount wordcount.zapp

You will notice in the output that the word counts from multiple files are
printed to the console.

.. _zebra-mapreduce-wordcount-sample:

Map/Reduce Word Count
"""""""""""""""""""""

This application builds on the concept of the previous example by applying a
classic map/reduce pattern to a word count problem. In the map phase we run a
wordcount on each file (just like :ref:`zebra-wordcount-sample`). The
difference here is in the reduce phase were we sum the total words in all files
and return a single result.

This sample also demonstrates a way to construct job pipelines and connect
groups of ZeroVM instances. See the ``connect`` section in the ``zapp.yaml``
configuration below.

Unlike previous examples, this application is designed to run only on
ZeroCloud, and not locally.

We can reuse the same input text files from :ref:`zebra-wordcount-sample` to
test this application.

1. Create the project directory
...............................

.. code-block:: bash

    $ mkdir ~/zebra/mrwordcount
    $ cd ~/zebra/mrwordcount

2. Add code
...........

This application consists of two separate scripts: one to count words in a
single document (``mrwordcount.py``) and one to reduce the word counts to a
single sum (``reducer.py``).

``mrwordcount.py``:

.. code-block:: python

    import os

    # Word count:
    with open('/dev/input') as fp:
        data = fp.read()

    with open('/dev/out/reducer', 'a') as fp:
        path_info = os.environ['PATH_INFO']

        # Split off the swift prefix
        # Just show the container/file
        shorter = '/'.join(path_info.split('/')[2:])
        # Pipe the output to the reducer:
        print >>fp, '%d %s' % (len(data.split()), shorter)

``reducer.py``:

.. code-block:: python

    import os
    import math

    inp_dir = '/dev/in'

    stdout = '/dev/stdout'

    total = 0
    max_count = 0

    data = []

    for inp_file in os.listdir(inp_dir):
        with open(os.path.join(inp_dir, inp_file)) as fp:
            for line in fp:
                count, filename = line.split()
                count = int(count)
                if count > max_count:
                    max_count = count
                data.append((count, filename))
                total += count

    fmt = '%%%sd %%s' % (int(math.log10(max_count)) + 2)

    for count, filename in data:
        print fmt % (count, filename)
    print fmt % (total, 'total')

3. Create a template zapp config file (``zapp.yaml``)
.....................................................

.. code-block:: bash

    $ zpm new

4. Customize the zapp config file
.................................

This configuration file will require more customization. The most significant
customizations are the addition of a ``reducer`` group and the ``connect``
directive for ``mrwordcount``. It should look like this:

.. code-block:: yaml

    execution:

      groups:
        - name: "mrwordcount"
          path: file://python:python
          args: "mrwordcount.py"
          connect: ["reducer"]
          devices:
          - name: python
          - name: stdout
          -
            name: input
            path: "swift://~/wordcount/text*.txt"

        - name: "reducer"
          path: file://python:python
          args: "reducer.py"
          devices:
          - name: python
          - name: stdout

    meta:
      Version: ""
      name: "mrwordcount"
      Author-email: ""
      Summary: ""

    help:
      description: ""
      args:
      - ["", ""]

    bundling:
      - "mrwordcount.py"
      - "reducer.py"


5. Test the application on ZeroCloud/Zebra
..........................................

.. code-block:: bash

    $ zpm bundle
    $ zpm deploy wordcount mrwordcount.zapp
    $ zpm execute wordcount mrwordcount.zapp

The output you get should look something like this::

     104 wordcount/text1.txt
     101 wordcount/text2.txt
      69 wordcount/text3.txt
     274 total
