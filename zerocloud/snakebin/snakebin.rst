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

- :ref:`Part 1: Upload/Download Scripts <snakebin_part1>`
- :ref:`Part 2: Execute Scripts <snakebin_part2>`
- :ref:`Part 3: Search Scripts <snakebin_part3>`

We will build the application in 3 parts. In the
:ref:`first part <snakebin_part1>`, we will implement a REST API for uploading
and downloading Python scripts to/from ZeroCloud. We will also implment a basic
UI to interact with the REST interface in HTML and JavaScript.

In the :ref:`second part <snakebin_part2>`, we will add a "Run" button to the
UI to remotely execute scripts on ZeroCloud. The secure isolation of ZeroVM
will ensure that any arbitrary code can run safely.

In the :ref:`third and final part <snakebin_part3>`, we will implement a
parallelized MapReduce-style search function for searching all existing
documents in Snakebin. The search function will be driven by a REST endpoint
and will include a "Search" field in the UI.


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

* ``snakebin``: This will serve as the base URL for REST API requests. This
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
a ZeroVM application (or "zapp"). We also want to include a basic
HTML/JavaScript UI template. ``zpm`` can do this for us:

.. code-block:: bash

    $ zpm new

This will create a ``zapp.yaml`` file in the current directory.

Open ``zapp.yaml`` in your favorite text editor.

Change the ``execution`` section

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

.. code-block:: yaml

    execution:
      groups:
        - name: ""
          path: file://python2.7:python
          args: ""
          devices:
          - name: python2.7
          - name: stdout
            content_type: message/http
          - name: stdin
          - name: input
            path: swift://~/snakebin-store

Change the ``help`` section

.. code-block:: yaml

    help:
      description: ""
      args:
      - ["", ""]

to look like this:

.. code-block:: yaml

    help:
      description: ""
      args: []

Edit the ``bundling`` section

.. code-block:: yaml

    bundling: []


to include the source files for our application (which we will be creating
below):

.. code-block:: yaml

    bundling: ["snakebin.py", "save_file.py", "get_file.py", "index.html"]

The final result should look like this:

.. literalinclude:: zapp.yaml


.. _snakebin_part1:

Part 1: Upload/Download Scripts
-------------------------------

First, we need to build an application for uploading and retrieving scripts,
complete with a basic HTML user interface.

Before we dig into the application code, we need to design our API.


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

    If a request specifies the header ``Accept: text/html``, load the HTML UI
    page with the script textarea populated. For any other ``Accept`` value,
    just return the raw script contents.


The Code
++++++++

ZeroCloud provides a CGI-like environment for servicing HTTP requests. A lot of
what follows involves setting and reading environment variables and generating
HTTP responses from scratch.


http_resp
.........

Since generating HTTP responses is the most crucial part of this application,
let's first define utility function for creating these responses. In your
``snakebin`` working directory, create a file called ``snakebin.py``. Then add
the following code to it:

.. literalinclude:: snakebin_part1.py
   :lines: 9,11-31
   :emphasize-lines: 22

Notice the last line, which is highlighted: ``sys.stdout.write(resp)``.

The ZeroCloud execution environment handles most communication between parts of
an application through ``/dev/stdout``, by convention. To your application code
(which is running inside the ZeroVM virtual execution environment),
``/dev/stdout`` looks just like the character device you would expect in a
Linux-like execution environment, but to ZeroCloud, you can write to this
device to communicate to a client or start a new "`job`", all using HTTP. (In
this tutorial, we'll be doing both.)

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

Let's create a class which will help us generate these jobs. Add the following
code to ``snakebin.py``. For simplicity, some Swift object/container names are
hard-coded.

.. literalinclude:: snakebin_part1.py
   :pyobject: Job

This class makes use of the ``json`` module, so lets add an import statement
to the top of the file:

.. literalinclude:: snakebin_part1.py
   :lines: 4


GET and POST handling
.....................

Now we're getting into the core functionality of our application. It's time to
add code to handle the ``POST`` and ``GET`` requests in the manner that we've
defined in our :ref:`API definition <snakebin_ul_dl_api>` above.

We'll need to add 4 new blocks of code:

- a function to handle ``POST`` requests
- a function to handle ``GET`` requests
- a utility function to check for file duplicates
- a "main" block to start the program and call the right handler function

.. literalinclude:: snakebin_part1.py
   :lines: 68-

This codes makes use of more standard library modules, so we need to add import
statements for those:

.. literalinclude:: snakebin_part1.py
   :lines: 1-3,5-8,10

Your ``snakebin.py`` file should now look something like this:

.. literalinclude:: snakebin_part1.py


``get_file.py`` and ``save_file.py``
....................................

In ``snakebin.py``, there are some references to additional source files to
handle saving and retrieval of uploaded documents. Let's create those now.

``get_file.py``:

.. literalinclude:: get_file_part1.py

``save_file.py``:

.. literalinclude:: save_file_part1.py


User Interface
..............

To complete the first evolution of the Snakebin application, let's a user
interface. Create a file called ``index.html`` and add the following code
to it:

.. literalinclude:: index_part1.html
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
    app deployed to http://127.0.0.1:8080/v1/AUTH_123def/snakebin-app/index.html

Configure the endpoint handler zapp for ``snakebin-api``, ``snakebin-app``, and
``snakebin-store``:

.. code-block:: bash

    $ swift post --header "X-Container-Meta-Rest-Endpoint: swift://AUTH_123def/snakebin-app/snakebin.zapp" snakebin-api
    $ swift post --header "X-Container-Meta-Rest-Endpoint: swift://AUTH_123def/snakebin-app/snakebin.zapp" snakebin-app
    $ swift post --header "X-Container-Meta-Rest-Endpoint: swift://AUTH_123def/snakebin-app/snakebin.zapp" snakebin-store

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
    http://127.0.0.1:8080/api/AUTH_123def/snakebin-api/GDHh7vR3Zb

The URL returned from the ``POST`` can be used to retrieve the document:

.. code-block:: bash

    $ curl http://127.0.0.1:8080/api/AUTH_123def/snakebin-api/GDHh7vR3Zb
    print "hello world!"

.. note:: Note that in the ``POST`` we have to supply the
    ``X-Zerovm-Execute: api/1.0`` header because this tells ZeroCloud how to
    interpret the request. Alternatively, you can change the ``/v1/`` part of
    the URL to ``/api/`` to make requests simpler, and also to accomodate
    simpler ``GET`` requests, using ``curl`` (as is shown above) or a web
    browser.

We can also try this through the web interface. Open a web browser and go to
``http://127.0.0.1:8080/api/AUTH_123def/snakebin-api``. You should get a page
that looks something like this:

.. image:: snakebin_part1_ui.png
   :width: 400

Type some text into the box and play around with saving documents. You can also
trying to browse the the document we created above on the command line
(``http://127.0.0.1:8080/api/AUTH_123def/snakebin-api/GDHh7vR3Zb``).

.. _snakebin_part2:

Part 2: Script Execution
------------------------

part2

.. _snakebin_part3:

Part 3: MapReduce Search
------------------------

part3
