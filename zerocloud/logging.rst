.. _logging:

Logging
=======

Most often, the types of problems you will need to troubleshoot have to do
specifically with your application code, and not the execution environment
itself. The ZeroCloud execution environment tends to be less verbose about
errors, in order to not leak potentially sensitive information to a client.
Showing stacktraces, for example, is not always a good idea.

The lack of verbosity is there for a reason, but this of course can make
troubleshooting and debugging difficult. This tutorial aims to illustrate
what types of errors are often encountered when developing applications for
ZeroCloud and what you can do catch and log these errors to aid you in
debugging.

Jump to a section:

- :ref:`Environment Setup <logging-setup>`
- :ref:`The stderr device <logging-stderr-device>`
- :ref:`Logging syntax errors <logging-syntax-errors>`
- :ref:`Logging exceptions <logging-exceptions>`
- :ref:`Explicit logging <logging-explicit>`

.. _logging-setup:

Environment Setup
-----------------

See :ref:`Setting up a development environment <devenv>` before continuing. If
you've already done this, feel free to jump ahead to the next section.

.. _logging-stderr-device:

The ``stderr`` device
---------------------

The best way to log information or errors in your application is to use the
``stderr`` device. We'll see how to do that by building a very simple "hello,
world"zapp. Just by adding ``stderr`` to the application config, any crashes
in the application code due to uncaught exceptions, or syntax errors will be
logged. We can also explicitly log information to ``stderr`` by writing to the
``sys.stderr`` device or to the file ``/dev/stderr``. In this guide, we'll go
through some examples to cover all of these cases.

To start with, create an application template with ``zpm``:

.. code-block:: bash

    $ zpm new
    Created './zapp.yaml'

Open ``zapp.yaml`` in your favorite text editor. Modify the ``meta`` section,
and set ``logtest`` for the name:

.. code-block:: yaml

    meta:
      Version: ""
      name: "logtest"
      Author-email: ""
      Summary: ""


Also modify the ``execution`` section, which by default looks something like
this:

.. code-block:: yaml

    execution:
      groups:
        - name: ""
          path: file://python2.7:python
          args: ""
          devices:
          - name: python2.7
          - name: stdout

Edit the ``execution`` section and give the execution a name, args, and a
``stderr`` device. For example:

.. code-block:: yaml
   :emphasize-lines: 3,5,9-10

    execution:
      groups:
        - name: "logtest"
          path: file://python2.7:python
          args: "logtest.py"
          devices:
          - name: python2.7
          - name: stdout
          - name: stderr
            path: swift://~/logs/logtest.log

The group name can be anything you like. For this example, we just call it
"logtest". The args should at least be the name of a Python script. We will
write that script below. For this example, we will just call it ``logtest.py``.

The ``stderr`` device is one of the special built-in devices that any ZeroCloud
application can use. We need to specify a Swift object path to write to in
order to capture error output. In this example, we've chosen ``logtest.log``
in the ``logs`` container.

Finally, modify the ``bundling`` the section to include ``logtest.py``:

.. code-block:: yaml

    bundling: ["logtest.py"]

.. _logging-syntax-errors:

Logging syntax errors
---------------------

Let's make our script into a basic "hello, world" application which has some
syntax errors. Create the file ``logtest.py`` and add the following code:

.. code-block:: python
    :emphasize-lines: 2

    print "hello, world"
    foo = [1, 2, 3
    print foo

The syntax error is the missing closing bracket on line 2.

Before we deploy, we'll need to create the ``log`` container:

.. code-block:: bash

    $ swift post logs

Now let's bundle, deploy, and run the application to see what happens:

.. code-block:: bash
   :emphasize-lines: 5

    $ zpm bundle
    created logtest.zapp
    $ zpm deploy logtest logtest.zapp
    $ curl -X POST -H "X-Zerovm-Execute: 1.0" -H "X-Zerovm-Source: swift://~/logtest/logtest.zapp" -H "X-Auth-Token: $OS_AUTH_TOKEN" $OS_STORAGE_URL
    (no output)

Notice that there is no output. Adding the ``-i/--include`` flag in the
``curl`` command will show us the HTTP response headers and give us a clue
about what went wrong.

.. code-block:: bash

    $ curl -i -X POST -H "X-Zerovm-Execute: 1.0" -H "X-Zerovm-Source: swift://~/logtest/logtest.zapp" -H "X-Auth-Token: $OS_AUTH_TOKEN" $OS_STORAGE_URL

The output should look something like this:

.. code-block:: bash
   :emphasize-lines: 2

    HTTP/1.1 200 OK
    X-Nexe-Retcode: 1
    X-Nexe-System: logtest
    X-Nexe-Cdr-Line: 2.289, 2.260, 0.04 2.00 1021 66644156 34 88 0 0 0 0
    X-Zerovm-Device: stdout
    X-Nexe-Policy: Policy-0
    X-Nexe-Validation: 2
    Content-Length: 0
    X-Nexe-Etag: /dev/stdout d41d8cd98f00b204e9800998ecf8427e
    Connection: close
    Etag: 433f8ee1c8da2c16bb625e87a1e89e7f
    X-Timestamp: 1415976829.81199
    X-Nexe-Status: ok
    Date: Fri, 14 Nov 2014 14:53:49 GMT
    Content-Type: text/html
    X-Chain-Total-Time: 2.289
    X-Trans-Id: txac6be961d72141ba9dbdf-005466177b

The most important line here is highlighted: ``X-Nexe-Retcode: 1``. This tells
us that our *application* (not the execution environment; this is an important
distinction) exited with a status code of 1. In other words, there was probably
a crash.

Let's download the log and see what it says:

.. code-block:: bash

    $ swift download logs logtest.log
    logtest.log [auth 0.030s, headers 0.038s, total 0.038s, 0.011 MB/s]
    $ cat logtest.log
      File "logtest.py", line 3
        print foo
            ^
    SyntaxError: invalid syntax

This is the same error output we would expect if we were to run ``logtest.py``
on local host:

.. code-block:: bash

    $ python logtest.py
      File "logtest.py", line 3
        print foo
            ^
    SyntaxError: invalid syntax

Fix the syntax error in ``logtest.py``:

.. code-block:: python
   :emphasize-lines: 2

    print "hello, world"
    foo = [1, 2, 3]
    print foo

Then re-bundle, re-deploy, and run:

.. code-block:: bash
   :emphasize-lines: 8

    $ zpm bundle
    Created logtest.zapp
    $ zpm deploy logtest logtest.zapp --force
    app deployed to
      http://127.0.0.1:8080/v1/AUTH_123def/logtest/
    $ curl -i -X POST -H "X-Zerovm-Execute: 1.0" -H "X-Zerovm-Source: swift://~/logtest/logtest.zapp" -H "X-Auth-Token: $OS_AUTH_TOKEN" $OS_STORAGE_URL
    HTTP/1.1 200 OK
    X-Nexe-Retcode: 0
    X-Nexe-System: logtest
    X-Nexe-Cdr-Line: 2.246, 2.229, 0.03 1.98 1021 66644156 11 23 0 0 0 0
    X-Zerovm-Device: stdout
    X-Nexe-Policy: Policy-0
    X-Nexe-Validation: 2
    Content-Length: 23
    X-Nexe-Etag: /dev/stdout c1def45af975364b4ee99d550d1d98da
    Connection: close
    Etag: d4c7b38bf909b5bc74eb81e73a5da81a
    X-Timestamp: 1415977445.97419
    X-Nexe-Status: ok
    Date: Fri, 14 Nov 2014 15:04:05 GMT
    Content-Type: text/html
    X-Chain-Total-Time: 2.246
    X-Trans-Id: tx40647fee812944ef80a99-00546619e3

    hello, world
    [1, 2, 3]

Note that the ``X-Nexe-Retcode`` is now ``0``, and we get the output we expect.

.. _logging-exceptions:

Logging exceptions
------------------

Let's try raising an exception to see what happens. Add one more line of code
to ``logtest.py``:

.. code-block:: python
   :emphasize-lines: 4

    print "hello, world"
    foo = [1, 2, 3]
    print foo
    raise Exception("test exception")

Re-bundle, re-deploy, and run:

.. code-block:: bash
   :emphasize-lines: 8

    $ zpm bundle
    Created logtest.zapp
    $ zpm deploy logtest logtest.zapp --force
    app deployed to
      http://127.0.0.1:8080/v1/AUTH_123def/logtest/
    $ curl -i -X POST -H "X-Zerovm-Execute: 1.0" -H "X-Zerovm-Source: swift://~/logtest/logtest.zapp" -H "X-Auth-Token: $OS_AUTH_TOKEN" $OS_STORAGE_URL
    HTTP/1.1 200 OK
    X-Nexe-Retcode: 1
    X-Nexe-System: logtest
    X-Nexe-Cdr-Line: 2.230, 2.211, 0.05 1.95 1021 66644156 19 163 0 0 0 0
    X-Zerovm-Device: stdout
    X-Nexe-Policy: Policy-0
    X-Nexe-Validation: 2
    Content-Length: 23
    X-Nexe-Etag: /dev/stdout c1def45af975364b4ee99d550d1d98da
    Connection: close
    Etag: a3afd778d9eafbf4d4429208d85aa35a
    X-Timestamp: 1415977837.42819
    X-Nexe-Status: ok
    Date: Fri, 14 Nov 2014 15:10:37 GMT
    Content-Type: text/html
    X-Chain-Total-Time: 2.230
    X-Trans-Id: txac87f5e842f04439b540c-0054661b6b

    hello, world
    [1, 2, 3]

This time we get the same output as above, but the ``X-Nexe-Retcode`` is ``1``.
Let's grab the log again to see what it says:

.. code-block:: bash

    $ swift download logs logtest.log
    logtest.log [auth 0.043s, headers 0.059s, total 0.060s, 0.009 MB/s]
    $ cat logtest.log
    Traceback (most recent call last):
      File "logtest.py", line 4, in <module>
        raise Exception("test exception")
    Exception: test exception

Similar to syntax errors, any uncaught/unhandled exceptions will be logged to
``stderr``.

.. _logging-explicit:

Explicit logging
----------------

Let's look at a case where we want to explicitly log something to ``stderr``.
We'll keep building on the code we have already in ``logtest.py``:

.. code-block:: python
   :emphasize-lines: 1,3,8-9

    import sys

    try:
        print "hello, world"
        foo = [1, 2, 3]
        print foo
        raise Exception("test exception")
    except Exception:
        sys.stderr.write("Something bad happened\n")

Here we are catching the exception and explictly logging a message instead of
letting the exception get logged (as we experienced above).

Let's test this to see what happens:

.. code-block:: bash
   :emphasize-lines: 8

    $ zpm bundle
    Created logtest.zapp
    $ zpm deploy logtest logtest.zapp --force
    app deployed to
      http://127.0.0.1:8080/v1/AUTH_123def/logtest/
    $ curl -i -X POST -H "X-Zerovm-Execute: 1.0" -H "X-Zerovm-Source: swift://~/logtest/logtest.zapp" -H "X-Auth-Token: $OS_AUTH_TOKEN" $OS_STORAGE_URL
    HTTP/1.1 200 OK
    X-Nexe-Retcode: 0
    X-Nexe-System: logtest
    X-Nexe-Cdr-Line: 2.258, 2.239, 0.07 1.94 1021 66644156 12 45 0 0 0 0
    X-Zerovm-Device: stdout
    X-Nexe-Policy: Policy-0
    X-Nexe-Validation: 2
    Content-Length: 23
    X-Nexe-Etag: /dev/stdout c1def45af975364b4ee99d550d1d98da
    Connection: close
    Etag: 83c1b9378a58e72a87f3cc82af081b67
    X-Timestamp: 1415980070.92201
    X-Nexe-Status: ok
    Date: Fri, 14 Nov 2014 15:47:50 GMT
    Content-Type: text/html
    X-Chain-Total-Time: 2.258
    X-Trans-Id: tx89ceb1b12459438ab9e8c-0054662424

    hello, world
    [1, 2, 3]

Note that the ``X-Nexe-Retcode`` is ``0``, meaning the application exited
gracefully.

Let's have a log at the log:

.. code-block:: bash

    $ swift download logs logtest.log
    logtest.log [auth 0.047s, headers 0.063s, total 0.065s, 0.001 MB/s]
    $ cat logtest.log
    Something bad happened

As an alternative to using the ``sys.stderr`` device, you can write logging
output to the file ``/dev/stderr``. The following code will behave the exact
same way as above:

.. code-block:: python
   :emphasize-lines: 7

    try:
        print "hello, world"
        foo = [1, 2, 3]
        print foo
        raise Exception("test exception")
    except Exception:
        with open("/dev/stderr", "a") as stderr:
            stderr.write("Something bad happened\n")

If you do it this way, note that you need to open the file with "append" mode
(`"a"`) specified.
