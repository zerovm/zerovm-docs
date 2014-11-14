.. _job-chaining:

Job Chaining
============

Applications executing on ZeroCloud have the potential to dynamically
start new jobs, allowing for arbitrary sequencing or "chaining" of programs.
Because each execution instance can only attach to a certain number of devices
(due to the data-local semantics of ZeroCloud computation), this allows your
program to read/write any number of various objects.

This tutorial will illustrate the basics of this feature and how to use it in
your application. In this example, we'll build an application with two scripts:
``script1.py`` and ``script2.py``. ``script1.py`` will be the entry point of
the application, which will chain-call a second job execution to run
``script2.py``.

You can chain-call as many jobs as you want in this manner, until the
``chain_timeout`` is reached. See `ZeroCloud job chaining configuration
<https://github.com/zerovm/zerocloud/blob/swift-2.0/doc/Configuration.md#job-chaining-middleware>`_
for more information.

For a more complex application which uses this feature, have a look at
:ref:`Example Application Tutorial: Snakebin <zerocloud-snakebin>`.

Jump to a section:

- :ref:`Environment Setup <jobchaining-setup>`
- :ref:`Create an application template <jobchaining-app-template>`
- :ref:`The code <jobchaining-the-code>`
- :ref:`Deploying the application <jobchaining-deploy>`
- :ref:`Running the application <jobchaining-run-app>`
- :ref:`Passing data through the call chain <jobchaining-passing-data>`

.. _jobchaining-setup:

Environment Setup
-----------------

See :ref:`Setting up a development environment <devenv>` before continuing. If
you've already done this, feel free to jump ahead to the next section.

.. _jobchaining-app-template:

Create an application template
------------------------------

To start building our application, we first need to create a ``zapp.yaml``
application template. ``zpm`` can do this for us:

.. code-block:: bash

    $ zpm new
    Created './zapp.yaml'

Open ``zapp.yaml`` in your favorite text editor and modify the ``execution``
section, which looks something like this:

.. code-block:: yaml

    execution:
      groups:
        - name: ""
          path: file://python2.7:python
          args: ""
          devices:
          - name: python2.7
          - name: stdout

Edit the ``execution`` section and define an execution group name and
arguments. We also need to modify the configuration of the ``stdout``
device to enable job chaining. For example:

.. code-block:: yaml
   :emphasize-lines: 3,5,9

    execution:
      groups:
        - name: "job-chain-test"
          path: file://python2.7:python
          args: "script1.py"
          devices:
          - name: python2.7
          - name: stdout
            content_type: message/http

The execution group name is just an arbitrary name. ``args`` needs to be at
least the name of a Python script to execute and can also include any
positional arguments. For the ``stdout`` device, we must add the content type
to enable special behavior for any content which is written to it.
``message/http`` indicates to the ZeroCloud middleware that the content can
either be interpreted as a new job request, or it can simply be a response to
the client. More on that later.

You will also need to define an application name in the ``meta`` section. For
simplicity, let's give the application the same name as the execution group:

.. code-block:: yaml
   :emphasize-lines: 3

    meta:
      Version: ""
      name: "job-chain-test"
      Author-email: ""
      Summary: ""

Finally, we'll need to include some code in the application. We'll add
:ref:`the code <jobchaining-the-code>` later, but for now we just need to tell
our ``zapp.yaml`` application config to include those source files when
bundling. Simply modify the ``bundling`` section to include our script file
names:

.. code-block:: yaml

    bundling: ["script1.py", "script2.py"]

.. _jobchaining-the-code:

The code
--------

Now that we've got our basic app configuration done, let's dig into the code.

Create a file called ``script1.py`` in the same directory as ``zapp.yaml`` and
add the following code:

.. code-block:: python
   :emphasize-lines: 18-24

    import json
    import sys

    job = json.dumps([{
        "name": "script2",
        "exec": {
            "path": "file://python2.7:python",
            "args": "script2.py"
        },
        "devices": [
            {"name": "python2.7"},
            {"name": "stdout"},
            {"name": "image",
             "path": "swift://~/chain/job-chain-test.zapp"},
        ],
    }])

    http_response = """\
    HTTP/1.1 200 OK\r
    Content-Type: application/json\r
    Content-Length: %(content_len)s\r
    X-Zerovm-Execute: 1.0
    \r
    %(content)s"""

    sys.stdout.write(http_response % dict(content=job, content_len=len(job)))

There are a couple of important things to highlight here. In order for
ZeroCloud to interpret the ``sys.stdout.write`` call as a job request:

- The status code and status reason don't too matter too much here. ``200 OK``
  is a good default, but the behavior is no different if you specify, for
  example, ``404 Not Found``.
- ``Content-Type`` *must* be ``application/json``
- ``X-Zerovm-Execute`` *must* be set to ``1.0``; this indicates to ZeroCloud
  that this is not just a normal HTTP response, but a special ZeroVM execution
  request.

.. note::

    The `HTTP specification
    <http://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Response_message>`_
    requires status line and header fields to end with a carriage return + line
    feed (\\r\\n). The \\n newline characters are implicit in multi-line string
    above, but the \\r carriage must be explicitly added. If you omit the \\r
    most clients probably won't complain, but it's best to follow the
    specification.

If ``X-Zerovm-Execute`` is omitted, this HTTP response would simply be sent
back to the client. This is the kind of response we'll be sending in
``script2.py``:

.. code-block:: python
   :emphasize-lines: 8

    import json
    import sys

    resp = json.dumps({"reply": "This is from script2.py"})

    http_response = """\
    HTTP/1.1 200 OK\r
    Content-Type: application/json\r
    Content-Length: %(content_len)s\r
    \r
    %(content)s"""

    sys.stdout.write(http_response % dict(content=resp, content_len=len(resp)))

A couple of things to highlight here:

- When writing a response intended for the client, you can use any
  ``Content-Type`` you like; it doesn't have to be ``application/json``.
  It can be ``text/plain``, ``text/html``, ``image/png``, etc.
- In fact, it doesn't even need to be properly structured HTTP text. For simple
  cases, you can simply just ``print`` text and it will get wrapped up in a
  proper HTTP response by ZeroCloud before sending it to the client. (It's just
  that writing proper HTTP yourself means your can return different statuses
  in different cases, like ``404 Not Found``, ``500 Internal Server Error``,
  etc.

.. _jobchaining-deploy:

Deploying the application
-------------------------

Time to bundle an deploy the application. First, bundle:

.. code-block:: bash

    $ zpm bundle
    created job-chain-test.zapp

For this example, we'll deploy the application to a container called ``chain``.
You can create this container first if you like (using ``swift post chain``),
or you can just let ``zpm deploy`` do it for you automatically.

.. code-block:: bash

    $ zpm deploy chain job-chain-test.zapp

.. _jobchaining-run-app:

Running the application
-----------------------

The easiest way to run the application is to send an HTTP request to ZeroCloud
using ``curl``:

.. code-block:: bash

    $ curl -X POST -H "X-Zerovm-Execute: 1.0" -H "X-Zerovm-Source: swift://~/chain/job-chain-test.zapp" -H "X-Auth-Token: $OS_AUTH_TOKEN" $OS_STORAGE_URL

The output should look like this:

.. code-block:: text

    HTTP/1.1 200 OK
    Content-Type: application/json
    Content-Length: 36

    {"reply": "This is from script2.py"}

Let's take a look at what's going on in this request.

- ``curl -X POST``: ZeroVM application execution requests are expected to use
  the ``POST`` method.
- ``-H "X-Zerovm-Execute: 1.0"``: This indicates to ZeroCloud that the ``POST``
  request should be interpreted as ZeroVM execution.
- ``-H "X-Zerovm-Source: swift://~/chain/job-chain-test.zapp"``: This indicates
  the application for ZeroCloud to execute. The ``job-chain-test.zapp``
  contains all the other information and code necessary to execute. The ``~``
  in the ``swift://`` path is an alias for your account ID. (The account ID is
  the ``$OS_STORAGE_ACCOUNT`` environment variable. See
  :ref:`Setting up a development environment <devenv>`.)
- ``-H "X-Auth-Token: $OS_AUTH_TOKEN"``: This is simply an auth token which
  Swift/ZeroCloud requires for us to access services. If you omit this, Swift
  will respond with a ``403 Unauthorized``.
- ``$OS_STORAGE_URL``: This is simply the destination for the ``POST`` request.

.. _jobchaining-passing-data:

Passing data through the call chain
-----------------------------------

If you want to pass data directly from one job to the next job in the call
chain, you can set environment variables in the job description. To illustrate
this, let's modify ``script1.py`` and ``script2.py``.

In ``script1.py``, we want to define some environment variables (``myvar`` and
``FOO``) to be set when ``script2.py`` executes:

.. code-block:: python
   :emphasize-lines: 9-12

    import json
    import sys

    job = json.dumps([{
        "name": "script2",
        "exec": {
            "path": "file://python2.7:python",
            "args": "script2.py",
            "env": {
                "FOO": "bar",
                "myvar": "12345",
            },
        },
        "devices": [
            {"name": "python2.7"},
            {"name": "stdout"},
            {"name": "image",
             "path": "swift://~/chain/job-chain-test.zapp"},
        ],
    }])

    http_response = """\
    HTTP/1.1 200 OK\r
    Content-Type: application/json\r
    Content-Length: %(content_len)s\r
    X-Zerovm-Execute: 1.0
    \r
    %(content)s"""

    sys.stdout.write(http_response % dict(content=job, content_len=len(job)))

.. TODO: blah blah talk about the env section

In ``script2.py``, let's read those variables from the environment and include
them in the client response:

.. code-block:: python
   :emphasize-lines: 2,5-7

    import json
    import os
    import sys

    resp_dict = {"reply": "This is from script2.py"}
    resp_dict["myvar"] = os.environ.get("myvar")
    resp_dict["FOO"] = os.environ.get("FOO")
    resp = json.dumps(resp_dict)

    http_response = """\
    HTTP/1.1 200 OK\r
    Content-Type: application/json\r
    Content-Length: %(content_len)s\r
    \r
    %(content)s"""

    sys.stdout.write(http_response % dict(content=resp, content_len=len(resp)))

To test this, first we need to re-bundle:

.. code-block:: bash

    $ zpm bundle

Then re-deploy:

.. code-block:: bash

    $ zpm deploy chain job-chain-test.zapp --force

.. note::

    We need to specify ``--force`` here since we're overwriting the previously
    deployed object.

To test the application, we can use the same ``curl`` command as before:

.. code-block:: bash

    $ curl -X POST -H "X-Zerovm-Execute: 1.0" -H "X-Zerovm-Source: swift://~/chain/job-chain-test.zapp" -H "X-Auth-Token: $OS_AUTH_TOKEN" $OS_STORAGE_URL

The output should look something like this:

.. code-block:: text

    HTTP/1.1 200 OK
    Content-Type: application/json
    Content-Length: 68

    {"myvar": "12345", "reply": "This is from script2.py", "FOO": "bar"}
