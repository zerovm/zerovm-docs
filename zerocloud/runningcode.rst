.. _running-code:

Running code on ZeroCloud
=========================

These examples below include executing code using just plain old ``curl``
commands on the command line, as well as scripting using Python and the
``requests`` (link?) module.

Getting an auth token
---------------------

The first thing you need to do is get an auth token and find the storage URL
for your account in Swift. For convenience, you can get this information simply
by running ``zpm auth``:

.. code-block:: bash

    $ zpm auth
    Auth token: PKIZ_Zrz_Qa5NJm44FWeF7Wp...
    Storage URL: http://127.0.0.1:8080/v1/AUTH_7fbcd8784f8843a180cf187bbb12e49c

Setting a couple of environment variables with these values will make commands
more concise and convenient to execute:

.. code-block:: bash

    $ export OS_AUTH_TOKEN=PKIZ_Zrz_Qa5NJm44FWeF7Wp...
    $ export OS_STORAGE_URL=http://127.0.0.1:8080/v1/AUTH_7fbcd8784f8843a180cf187bbb12e49c

POST a Python script
--------------------

This is the simplest and easiest way to execute code on ZeroCloud.

First, write the following the code into a file called ``example``.

.. code-block:: python

    #!file://python2.7:python
    import sys
    print("Hello from ZeroVM!")
    print("sys.platform is '%s'" % sys.platform)

Execute it using ``curl``:

.. code-block:: bash

    $ curl -i -X POST -H "X-Auth-Token: $OS_AUTH_TOKEN" -H "X-Zerovm-Execute: 1.0" -H "Content-Type: application/python" --data-binary @example $OS_STORAGE_URL


Using a Python script:

.. code-block:: python

    import os
    import requests

    storage_url = os.environ.get('OS_STORAGE_URL')
    headers = {
        'X-Zerovm-Execute': 1.0,
        'X-Auth-Token': os.environ.get('OS_AUTH_TOKEN'),
        'Content-Type': 'application/python',
    }

    with open('example') as fp:
        response = requests.post(storage_url,
                                 data=fp.read(),
                                 headers=headers)
        print(response.content)

You can write and execute any Python code in this way, using any of the modules
in the standard library.

POST a ZeroVM image
-------------------

Another way to execute code on ZeroCloud is to create a specially constructed
tarball (a "ZeroVM image") and ``POST`` it directly to ZeroCloud.  A "ZeroVM
image" is a tarball with at minimum a ``boot/system.map`` file. The
``boot/system.map``, or job description, contains runtime execution information
which tells ZeroCloud what to execute.

This is useful if your code consists of multiple source files (not just a
single script). You can pack everything into a single file and execute it.

In this example, we'll do just that. Create the following files:

mymath.py:

.. code-block:: python

    def add(a, b):
        return a + b

main.py:

.. code-block:: python

    import mymath
    a = 5
    b = 6
    the_sum = mymath.add(a, b)
    print("%s + %s = %s" % (a, b, the_sum))

boot/system.map:

.. code-block:: javascript

    [{
        "name": "example",
        "exec": {
            "path": "file://python2.7:python",
            "args": "main.py"
        },
        "devices": [
            {"name": "python2.7"},
            {"name": "stdout"}
        ]
    }]

Create the ZeroVM image:

.. code-block:: bash

    $ tar cf example.tar boot/system.map main.py mymath.py

Execute the ZeroVM image directly on ZeroCloud using ``curl``:

.. code-block:: bash

    $ curl -i -X POST -H "Content-Type: application/x-tar" -H "X-Auth-Token: $OS_AUTH_TOKEN" -H "X-Zerovm-Execute: 1.0" --data-binary @example.tar $OS_STORAGE_URL

Using a Python script:

.. code-block:: python

    import os
    import requests

    storage_url = os.environ.get('OS_STORAGE_URL')
    headers = {
        'X-Zerovm-Execute': 1.0,
        'X-Auth-Token': os.environ.get('OS_AUTH_TOKEN'),
        'Content-Type': 'application/x-tar',
    }

    with open('example.tar') as fp:
        response = requests.post(storage_url,
                                 data=fp.read(),
                                 headers=headers)
        print(response.content)

POST a job description to a ZeroVM application (zapp)
-----------------------------------------------------

TODO
