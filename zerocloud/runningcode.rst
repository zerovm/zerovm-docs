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

    $ curl -i -X POST -H "X-Auth-Token: $OS_AUTH_TOKEN" \
      -H "X-Zerovm-Execute: 1.0" -H "Content-Type: application/python" \
      --data-binary @example $OS_STORAGE_URL


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
This method is also useful if you want to just execute something once, meaning
that once ZeroCloud executes the application, the app is thrown away.

In this example, we'll do just that. Create the following files:

``mymath.py``:

.. code-block:: python

    def add(a, b):
        return a + b

``main.py``:

.. code-block:: python

    import mymath
    a = 5
    b = 6
    the_sum = mymath.add(a, b)
    print("%s + %s = %s" % (a, b, the_sum))

Create a ``boot`` directory, then ``boot/system.map`` file:

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

    $ curl -i -X POST -H "Content-Type: application/x-tar" \
      -H "X-Auth-Token: $OS_AUTH_TOKEN" -H "X-Zerovm-Execute: 1.0" \
      --data-binary @example.tar $OS_STORAGE_URL

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

POST a job description to a ZeroVM application
----------------------------------------------

This method is useful if you want to execute the same application multiple
times, for example, to run an application to process multiple different files.

In this example, we will upload a packaged application into Swift and then
subsequently POST job descriptions to execute the application. This can be done
multiple times, and with different arguments. We'll use this to build a small
application. Create a directory ``sampleapp`` and in it, create the following files:

``main.py``:

.. code-block:: python

    import csv
    with open('/dev/input') as fp:
        reader = csv.reader(fp)

        for id, name, email, balance in reader:
            print('%(name)s: %(balance)s' % dict(name=name, balance=balance))

Create an ``example.tar`` containing the Python script:

.. code-block:: bash

    $ tar cf example.tar main.py

Create a container for the application:

.. code-block:: bash

    $ swift post example

Upload the image into Swift:

.. code-block:: bash

    $ swift upload example example.tar

Now we need to create a couple of files for the application to read and process.

``data1.csv``:

.. code-block:: text

    id,name,email,balance
    1,Alice,alice@example.com,1000
    2,Bob,bob@example.com,-500

``data2.csv``:

.. code-block:: text

    id,name,email,balance
    3,David,david@example.com,15000
    4,Erin,erin@example.com,25000

Upload the data files into Swift:

.. code-block:: bash

    $ swift upload example data1.csv data2.csv

``job.json``:

.. code-block:: javascript

    [{
        "name": "example",
        "exec": {
            "path": "file://python2.7:python",
            "args": "main.py"
        },
        "devices": [
            {"name": "python2.7"},
            {"name": "stdout"},
            {"name": "input", "path": "swift://~/example/data1.csv"},
            {"name": "image", "path": "swift://~/example/example.tar"}
        ]
    }]

Execute it using ``curl``:

.. code-block:: bash

    $ curl -i -X POST -H "Content-Type: application/json" \
      -H "X-Auth-Token: $OS_AUTH_TOKEN" -H "X-Zerovm-Execute: 1.0" \
      --data-binary @job.json $OS_STORAGE_URL

Execute it using a Python script:

.. code-block:: python

    import os
    import requests

    storage_url = os.environ.get('OS_STORAGE_URL')
    headers = {
        'X-Zerovm-Execute': 1.0,
        'X-Auth-Token': os.environ.get('OS_AUTH_TOKEN'),
        'Content-Type': 'application/json',
    }

    with open('job.json') as fp:
        response = requests.post(storage_url,
                                 data=fp.read(),
                                 headers=headers)
        print(response.content)

You can process a different input file by simply changing the ``job.json`` and
re-running the application (using ``curl`` or the Python script above). For
example, change this line

.. code-block:: text

    {"name": "input", "path": "swift://~/example/data1.csv"},

to this:

.. code-block:: text

    {"name": "input", "path": "swift://~/example/data2.csv"},

Your ``job.json`` file should now look like this:

.. code-block:: javascript

    [{
        "name": "example",
        "exec": {
            "path": "file://python2.7:python",
            "args": "main.py"
        },
        "devices": [
            {"name": "python2.7"},
            {"name": "stdout"},
            {"name": "input", "path": "swift://~/example/data2.csv"},
            {"name": "image", "path": "swift://~/example/example.tar"}
        ]
    }]

Try running that and see the difference in the output:

.. code-block:: bash

    $ curl -i -X POST -H "Content-Type: application/json" \
      -H "X-Auth-Token: $OS_AUTH_TOKEN" -H "X-Zerovm-Execute: 1.0" \
      --data-binary @job.json $OS_STORAGE_URL

Run a ZeroVM application with an object GET
-------------------------------------------

It is possible to attach applications to particular types of objects and run
that application when the object is retrieved (using a GET request) from Swift.

In this example, we'll write an application which processes JSON file objects and
returns a pretty-printed version of the contents. The idea here is that we take
some raw JSON data and make it more human-readable.

Create the following files in a new directory ``sampleapp2``:

``data.json``:

.. code-block:: javascript

    {"type": "GeometryCollection", "geometries": [{ "type": "Point", "coordinates": [100.0, 0.0]}, {"type": "LineString", "coordinates": [[101.0, 0.0], [102.0, 1.0]]}]}

``prettyprint.py``:

.. code-block:: python

    import json
    import pprint

    with open('/dev/input') as fp:
        data = json.load(fp)
        print(pprint.pformat(data))

``config``:

.. code-block:: javascript

    [{
        "name": "prettyprint",
        "exec": {
            "path": "file://python2.7:python",
            "args": "prettyprint.py"
        },
        "devices": [
            {"name": "python2.7"},
            {"name": "stdout"},
            {"name": "input", "path": "{.object_path}"},
            {"name": "image", "path": "swift://~/example/prettyprint.tar"}
        ]
    }]


Upload the test data:

.. code-block:: bash

    $ swift post example  # creates the container, if it doesn't exist already
    $ swift upload example data.json

Bundle and upload the application:

.. code-block:: bash

    $ tar cf prettyprint.tar prettyprint.py
    $ swift upload example prettyprint.tar

Upload the configuration to a ``.zvm`` container:

.. code-block:: bash

    $ swift post .zvm  # creates the container, if it doesn't exist already
    $ swift upload .zvm config --object-name=application/json/config

Now submit a GET request to the file, and it will be processed by the
``prettyprint`` application. Setting the ``X-Zerovm-Execute`` header to
``open/1.0`` is required to make this work. (Without this header you'll just
get the raw file, unprocessed.)

Using ``curl``:

.. code-block:: bash

    $ curl -i -X GET $OS_STORAGE_URL/example/data.json \
      -H "X-Zerovm-Execute: open/1.0" -H "X-Auth-Token: $OS_AUTH_TOKEN"

Using a Python script:

.. code-block:: python

    import os
    import requests

    storage_url = os.environ.get('OS_STORAGE_URL')
    headers = {
        'X-Zerovm-Execute': 'open/1.0',
        'X-Auth-Token': os.environ.get('OS_AUTH_TOKEN'),
    }

    response = requests.get(storage_url + '/example/data.json',
                            headers=headers)
    print(response.content)
