.. _zerocloud-snakebin:

Example Application Tutorial: Snakebin
======================================

Snakebin is a combination of `Pastebin <http://pastebin.com>`_
and `JSFiddle <http://jsfiddle.net/>`_, for Python. It allows a user to create
and store Python scripts in ZeroCloud, retrieve them using a unique URL, and
execute them through a web interface. Essentially this is a copy of the
`Go Playground <http://play.golang.org>`_, but for Python.

In this tutorial, we will be building the entire application from scratch and
deploying it to ZeroCloud. The result will be a web application, complete with
a REST API and a basic UI written in HTML and JavaScript. The entire backend
for the REST API will be implemented in Python.


Overview
--------

Jump to a section:

- :ref:`Part 1: Upload/Download Scripts <snakebin_part1>`
- :ref:`Part 2: Execute Scripts <snakebin_part2>`
- :ref:`Part 3: Search Scripts <snakebin_part3>`

We will build the application in three parts. In the
:ref:`first part <snakebin_part1>`, we will implement a REST API for uploading
and downloading Python scripts to/from ZeroCloud. We will also implment a basic
UI to interact with the REST interface in HTML and JavaScript.

In the :ref:`second part <snakebin_part2>`, we will add execution
functionality to the API, as well as a "Run" button to the UI to execute code.
The secure isolation of ZeroVM will ensure that any arbitrary code can run
safely.

In the :ref:`third and final part <snakebin_part3>`, we will implement a
parallelized MapReduce-style search function for searching all existing
documents in Snakebin. The search function will be driven by yet another
addition to the API and will include a "Search" field in the UI.


Setup
-----

The first thing you'll need to do is set up a
:ref:`development environment <devenv>`, including the ``python-swiftclient``
and ``zpm`` command line tools.

Next, you should create a working directory on your local machine. In this
tutorial, we will put all project files in a directory called ``snakebin``
inside the home directory. Change to this directory as well.

.. code-block:: bash

    $ mkdir $HOME/snakebin
    $ cd $HOME/snakebin


Swift Container Setup
---------------------

To deploy and run the application, we'll need three containers:

* ``snakebin-api``: This will serve as the base URL for REST API requests. This
  container will only contain the HTML / JavaScript UI files.
* ``snakebin-app``: This will contain all of the application files, except for
  the UI files.
* ``snakebin-store``: This will serve as our document storage location. No
  direct access will be allowed; all documents must be accessed through the
  REST API.

Go ahead and create these containers now. You can do this using the ``swift``
command line tool:

.. code-block:: bash

    $ swift post snakebin-api
    $ swift post snakebin-app
    $ swift post snakebin-store

Double-check that the containers were created:

.. code-block:: bash

    $ swift list
    snakebin-api
    snakebin-app
    snakebin-store


Add ``zapp.yaml``
-----------------

The next thing we need to do is add the basic configuration file which defines
a ZeroVM application (or "zapp"). ``zpm`` can do this for us:

.. code-block:: bash

    $ zpm new --template python

This will create a ``zapp.yaml`` file in the current directory. Open
``zapp.yaml`` in your favorite text editor. Change the ``execution`` section

.. code-block:: yaml

    execution:
      groups:
        - name: ""
          path: file://python2.7:python
          args: ""
          devices:
          - name: python2.7
          - name: stdout

to look like this:

.. literalinclude:: part1/zapp.yaml
    :language: yaml
    :lines: 3-14
    :emphasize-lines: 3,5,9-12

Edit the ``bundling`` section

.. code-block:: yaml

    bundling: []

to include the source files for our application (which we will be creating
below):

.. literalinclude:: part1/zapp.yaml
    :language: yaml
    :lines: 26

Finally, we need to specify third-party dependencies so that ``zpm`` knows how
to bundle our application:

.. literalinclude:: part1/zapp.yaml
    :language: yaml
    :lines: 28-32

The final result should look like this:

.. literalinclude:: part1/zapp.yaml
   :language: yaml


.. _snakebin_part1:

Part 1: Upload/Download Scripts
-------------------------------

First, we need to build an application for uploading and retrieving scripts,
complete with a basic HTML user interface.

Before we dig into the application code, let's think about our API design.

.. _snakebin_ul_dl_api:

REST API
++++++++

For the time being, we only need to support a few different types of requests:

``GET /snakebin-api``:
    Get an empty HTML form for uploading a script.

``POST /snakebin-api``:
    Post file contents, get a ``/snakebin-api/:script`` URL back.

``GET /snakebin-api/:script``:
    Retrieve uploaded file contents.

    If a request specifies the header ``Accept: text/html`` (as is the case
    with a web browser), load the HTML UI page with the script textarea
    populated. For any other ``Accept`` value, just return the raw script
    contents.


The Code
++++++++

ZeroCloud provides a CGI-like environment for handling HTTP requests. A lot of
what follows involves setting and reading environment variables and generating
HTTP responses from scratch.


http_resp
.........

Since generating HTTP responses is the most crucial part of this application,
let's first define utility function for creating these responses. In your
``snakebin`` working directory, create a file called ``snakebin.py``. Then add
the following code to it:

.. literalinclude:: part1/snakebin.py
   :pyobject: http_resp
   :emphasize-lines: 19


Notice the last line, which is highlighted: ``sys.stdout.write(resp)``.

The ZeroCloud execution environment handles most communication between parts of
an application through ``/dev/stdout``, by convention. To your application code
(which is running inside the ZeroVM virtual execution environment),
``/dev/stdout`` looks just like the character device you would expect in a
Linux-like execution environment, but to ZeroCloud, you can write to this
device to either communicate to a client or start a new "`job`", all using HTTP.
(In this tutorial, we'll be doing both.)

For ``http_resp``, we'll need to import ``sys`` from the standard library. Add
an ``import`` statement to the top of the file:

.. code-block:: python

    import sys


Job
...

A "`job`" is defined by a collection of JSON objects which specify commands
to execute, environment variables to set (for the execution environment),
and device mappings. ZeroCloud consumes job descriptions to start new
jobs, which can consist of one or more program execution groups. For the
moment, we'll only be dealing with single program jobs. (In
:ref:`part three <snakebin_part3>`, we'll need to define some multi-group
jobs to implement the MapReduce search function. But don't worry about that
for now.)

.. tip:: For complete details on structure and options for a job description,
    check out the `full documentation
    <https://github.com/zerovm/zerocloud/blob/swift-2.0/doc/Servlets.md>`_.

Let's create a class which will help us generate these jobs. Add the class
below to ``snakebin.py``. For simplicity, some Swift object/container names are
hard-coded.

.. literalinclude:: part1/snakebin.py
   :pyobject: Job

This class makes use of the ``json`` module, so lets import that as well:

.. code-block:: python

    import json


GET and POST handling
.....................

Now we're getting into the core functionality of our application. It's time to
add code to handle the ``POST`` and ``GET`` requests in the manner that we've
defined in our :ref:`API definition <snakebin_ul_dl_api>` above.

To make things easy for us, we can write this functionality as a `WSGI
application <https://www.python.org/dev/peps/pep-0333/>`_ and use light-weight
API framework like `Falcon <https://github.com/racker/falcon>`_ to implement
the various endpoint handlers.

We'll need to add a handful of new things to ``snakebin.py``:

- a utility function to query container databases to check if an object with a
  given name already exists
- a utility function to generate a random "short name", using script upload
  contents as the random seed
- a couple of "handler" classes and some helper functions for dealing with the
  various types of requests
- a ``main`` block which sets up the WSGI application and registers the
  endpoint handlers

Here's what that looks like:

.. literalinclude:: part1/snakebin.py
   :lines: 74-

This codes makes use of more standard library modules, so we need to add import
statements for those, as well as `falcon <https://github.com/racker/falcon>`_,
a third party library.

.. literalinclude:: part1/snakebin.py
    :lines: 1-12
    :emphasize-lines: 1-2,4-7,9-12

Your ``snakebin.py`` file should now look something like this:

.. literalinclude:: part1/snakebin.py


``get_file.py`` and ``save_file.py``
....................................

In ``snakebin.py``, there are some references to additional source files to
handle saving and retrieval of uploaded documents. Let's create those now.

``get_file.py``:

.. literalinclude:: part1/get_file.py

``save_file.py``:

.. literalinclude:: part1/save_file.py


User Interface
..............

To complete the first iteration of the Snakebin application, let's create a
user interface. Create a file called ``index.html`` and add the following code
to it:

.. literalinclude:: part1/index.html
   :language: html

Bundle and deploy
+++++++++++++++++

Bundle:

.. code-block:: bash

    $ zpm bundle
    created snakebin.zapp

Deploy:

.. code-block:: bash

    $ zpm deploy snakebin-app snakebin.zapp
    app deployed to http://127.0.0.1:8080/v1/AUTH_123def/snakebin-app/

Setting an environment variable for the storage account ID will make commands
more concise and convenient to execute:

.. code-block:: bash

    $ export OS_STORAGE_ACCOUNT=AUTH_123def...

Configure the endpoint handler zapp for ``snakebin-api``, ``snakebin-app``, and
``snakebin-store``:

.. code-block:: bash

    $ swift post --header "X-Container-Meta-Rest-Endpoint: swift://$OS_STORAGE_ACCOUNT/snakebin-app/snakebin.zapp" snakebin-api
    $ swift post --header "X-Container-Meta-Rest-Endpoint: swift://$OS_STORAGE_ACCOUNT/snakebin-app/snakebin.zapp" snakebin-app
    $ swift post --header "X-Container-Meta-Rest-Endpoint: swift://$OS_STORAGE_ACCOUNT/snakebin-app/snakebin.zapp" snakebin-store

We'll also need to set execution permissions for unauthenticated (anonymous)
users on the same three containers:

.. code-block:: bash

    $ swift post --header "X-Container-Meta-Zerovm-Suid: .r:*,.rlistings" snakebin-api
    $ swift post --header "X-Container-Meta-Zerovm-Suid: .r:*,.rlistings" snakebin-app
    $ swift post --header "X-Container-Meta-Zerovm-Suid: .r:*,.rlistings" snakebin-store


Test
++++

Now that the first working part of our application is deployed, let's test
uploading and retrieving some text.

First, create a file called ``example.py``, and add any text to it. For
example:

.. code-block:: python

    print "hello world!"

Now upload it:

.. code-block:: bash

    $ curl -X POST -H "X-Zerovm-Execute: api/1.0" $OS_STORAGE_URL/snakebin-api --data-binary @example.py
    http://127.0.0.1:8080/api/$OS_STORAGE_ACCOUNT/snakebin-api/GDHh7vR3Zb

The URL returned from the ``POST`` can be used to retrieve the document:

.. code-block:: bash

    $ curl http://127.0.0.1:8080/api/$OS_STORAGE_ACCOUNT/snakebin-api/GDHh7vR3Zb
    print "hello world!"

.. note:: Note that in the ``POST`` we have to supply the
    ``X-Zerovm-Execute: api/1.0`` header because this tells ZeroCloud how to
    interpret the request. Alternatively, you can change the ``/v1/`` part of
    the URL to ``/api/`` to make requests simpler, and also to accomodate
    simpler ``GET`` requests, using ``curl`` (as is shown above) or a web
    browser.

We can also try this through the web interface. Open a web browser and go to
``http://127.0.0.1:8080/api/$OS_STORAGE_ACCOUNT/snakebin-api``. You should get a
page that looks something like this:

.. image:: snakebin_part1_ui.png
   :width: 400

Type some text into the box and play around with saving documents. You can also
try to browse the the document we created above on the command line
(``http://127.0.0.1:8080/api/$OS_STORAGE_ACCOUNT/snakebin-api/GDHh7vR3Zb``).

.. _snakebin_part2:

Part 2: Execute Scripts
-----------------------

In this part, we'll add on to what we've built so far and allow Python scripts
to be executed by Snakebin.

API updates
+++++++++++

To support script execution via HTTP (either from the command line or browser),
we will need to add a couple more endpoints to our API:

``GET /snakebin-api/:script/execute``:
    Execute the specified ``:script`` and return the output as text.
    The script must already exist and be available at
    ``/snakebin-api/:script``.

``POST /snakebin-api/execute``:
    Execute the contents of the request as a Python script and return the
    output as text.

The following changes will implement these two endpoints.

The Code
++++++++

We need to add a couple of things to support script execution. First, we need
to add a utility function to just execute code, and second, we need to update
the endpoint handlers to support execution.

First, we need to tweak ``_handle_script`` to support execution:

.. literalinclude:: part2/snakebin.py
    :pyobject: _handle_script
    :emphasize-lines: 1,9-10

Next, add an ``execute_code`` utility function, which actually do the execution:

.. literalinclude:: part2/snakebin.py
    :pyobject: execute_code

``execute_code`` requires the ``imp`` and ``StringIO`` standard library modules,
so we need to import those:

.. literalinclude:: part2/snakebin.py
    :lines: 1-14
    :emphasize-lines: 3,9

Next, update the ``ScriptHandler`` class (to support direct POSTing of scripts
for execution):

.. literalinclude:: part2/snakebin.py
    :pyobject: ScriptHandler
    :emphasize-lines: 7-

and add a new ``ScriptExecuteHandler`` class:

.. literalinclude:: part2/snakebin.py
    :pyobject: ScriptExecuteHandler

Finally, we need to register the new handler (and add a comment to explain some
new behavior for ``ScriptHandler``):

.. literalinclude:: part2/snakebin.py
    :lines: 224-
    :emphasize-lines: 4,6-7

Now we need to make some modifications to ``get_file.py`` to allow execution
of a script. We need to read the ``SNAKEBIN_EXECUTE`` environment variable
and execute a script if it is present. Update ``get_file.py`` to this:

.. literalinclude:: part2/get_file.py
   :emphasize-lines: 12,15-25,30-33

We now need to update the UI with a "Run" button to hook in the execution
functionality. Update your ``index.html`` to look like this:

.. literalinclude:: part2/index.html
   :language: html
   :emphasize-lines: 42-68,77,80-85


Redeploy the application
++++++++++++++++++++++++

First, rebundle your application files:

.. code-block:: bash

    $ zpm bundle

To redeploy, we'll use the same ``zpm`` command as before, but we'll need to
specify the ``--force`` flag, since we're deploying to an un-empty container:

.. code-block:: bash

    $ zpm deploy snakebin-app snakebin.zapp --force

Test
++++

First, let's try executing one of the scripts we already uploaded. This can be
done simply by ``curl``ing the URL of the script and appending ``/execute``:

.. code-block:: bash

    $ curl http://127.0.0.1:8080/api/$OS_STORAGE_ACCOUNT/snakebin-api/GDHh7vR3Zb/execute
    hello world!

Next, let's trying posting the ``example.py`` script directly to the
``/snakebin-api/execute`` endpoint:

.. code-block:: bash

    $ curl -X POST http://127.0.0.1:8080/api/$OS_STORAGE_ACCOUNT/snakebin-api/execute --data-binary @example.py
    hello world!

Let's also test the functionality in the web browser. If you nagivate to
``http://127.0.0.1:8080/api/$OS_STORAGE_ACCOUNT/snakebin-api``, the new page
should look something like this:

.. image:: snakebin_part2_ui.png
   :width: 400

Try writing some code into the text box and click ``Run`` to execute them.

Try also accessing the ``/snakebin-api/:script/execute`` endpoint directly
in the browser using the same the URL in the POST example above:

``http://127.0.0.1:8080/api/$OS_STORAGE_ACCOUNT/snakebin-api/GDHh7vR3Zb/execute``

.. _snakebin_part3:

Part 3: Search Scripts
----------------------

The final piece of Snakebin is a simple search search mechanism, which will find
document which contain a given search term. All documents in ``snakebin-store``
will be searched in a parallelized fashion using the MapReduce semantics of
ZeroCloud.

API updates
+++++++++++

The final endpoint we'll add to our API is ``search``:

``GET /snakebin-api/search?q=:term``:
    Return a JSON list of URLs to the documents (in ``snakebin-store``)
    which contain ``:term``. When this endpoint is hit, a MapReduce job of
    multiple nodes will be spawned to perform the search.

The Code
++++++++

For the MapReduce job, we need to add two new Python modules.

``search_mapper.py``

.. literalinclude:: part3/search_mapper.py

``search_reducer.py``

.. literalinclude:: part3/search_reducer.py

These two files will handle the bulk of the search operation.

To kick off the search, we need to make some more changes to
``snakebin.py``. First, add a ``_handle_search`` utility function:

.. literalinclude:: part3/snakebin.py
    :pyobject: _handle_search

``_handle_search`` needs the ``urllib`` module from the standard library, so we
must import it:

.. literalinclude:: part3/snakebin.py
    :lines: 1-15
    :emphasize-lines: 11

Finally, we need to make one small tweak to ``ScriptHandler`` to hook in the
search function:

.. literalinclude:: part3/snakebin.py
    :pyobject: ScriptHandler
    :emphasize-lines: 4-7

Now for the final changes to the user interface:

.. literalinclude:: part3/index.html
   :language: html
   :emphasize-lines: 69-92,97-102

We also need to update the ``zapp.yaml`` to include the new Python files.
Update the bundling section:

.. code-block:: yaml

    bundling: ["snakebin.py", "save_file.py", "get_file.py", "index.html",
               "search_mapper.py", "search_reducer.py"]

Redeploy the application
++++++++++++++++++++++++

Just as we did before in :ref:`part 2 <snakebin_part2>`, we need to redeploy
the application, using ``zpm``:

.. code-block:: bash

    $ zpm bundle
    $ zpm deploy snakebin-app snakebin.zapp --force

Test
++++

First, let's try executing the search on the command line. (You should post
a couple of a scripts to Snakebin first, otherwise your search won't return
anything, obviously.)

.. code-block:: bash

    $ curl http://127.0.0.1:8080/api/$OS_STORAGE_ACCOUNT/snakebin-api/search?q=foo
    ["http://127.0.0.1:8080/api/$OS_STORAGE_ACCOUNT/snakebin-api/IOFW0Z8UYR", "http://127.0.0.1:8080/api/$OS_STORAGE_ACCOUNT/snakebin-api/e2X0hNA9ld"]

Let's also test the functionality in the web browser. If you navigate to
``http://127.0.0.1:8080/api/$OS_STORAGE_ACCOUNT/snakebin-api``, the new page
should look something like this:

``http://127.0.0.1:8080/api/$OS_STORAGE_ACCOUNT/snakebin-api``, the new page
should look something like this:

.. image:: snakebin_part3_ui.png
   :width: 400

Try typing in a search term and clicking "Search".

Try also accessing the ``/snakebin-api/search?q=:term`` endpoint directly in
the browser.
