.. _devenv:

Setting up a development environment
==============================================

The easiest way to get up and running is to install and run ZeroCloud on
`DevStack <http://devstack.org/>`_ inside VirtualBox. We provide some
`Vagrant <http://www.vagrantup.com>`_ scripts to make the setup require little
effort.

With this environment, you can not only write and run applications on
ZeroCloud, but you can also hack on ZeroCloud on itself.

Note to Linux users: There should be packages available (using the favored
package manager of your distro) for just about everything you need to install.

Install VirtualBox
------------------

Download and install VirtualBox: https://www.virtualbox.org/wiki/Downloads.

Install Vagrant
---------------

Download and install Vagrant: https://www.vagrantup.com/downloads.html.

Clone the ZeroCloud source code
-------------------------------

First, you'll need to download and install Git: http://git-scm.com/downloads

From a command line, clone the soure code. In this example, we just checkout
the code into a ``zerocloud`` folder in our home directory.

.. code-block:: bash

    $ git clone https://github.com/zerovm/zerocloud.git $HOME/zerocloud

vagrant up
----------

Now we can actually start OpenStack Swift and ZeroCloud, inside a VM:

.. code-block:: bash

    $ cd $HOME/zerocloud/contrib/vagrant
    $ vagrant up

``vagrant up`` will download and install DevStack and configure it to run
Swift with the ZeroCloud middleware. This usually takes about 10-15 minutes.

After the initial installation, you'll need restart DevStack and ZeroCloud.
To do so, first log in to the the vagrant box:

.. code-block:: bash

    $ vagrant ssh

Next, we need to terminate all of the DevStack processes. The first time you do
this, you need to use a little brute force. First, run rejoin-stack.sh:

.. code-block:: bash

    $ cd $HOME/devstack
    $ ./rejoin-stack.sh

This will put you into a screen session. To terminate DevStack, press
'ctrl+a backslash', then 'y' to confirm. NOTE: The first time you restart
DevStack after provisioning the machine, not all of the Swift processes will
be killed. A little brute force is needed:

.. code-block:: bash

    $ ps ax | grep [s]wift | awk '{print $1}' | xargs kill

Now restart DevStack:

.. code-block:: bash

    $ cd $HOME/devstack
    $ ./rejoin-stack.sh

If you make configuration changes after this first DevStack restart, subsequent
restarts are easier. Run ``./rejoin-stack.sh`` as above, press
'ctrl+a backslash', 'y' to confirm, then run ``./rejoin-stack.sh`` again.

To log out of the vagrant box and keep everything running, press 'ctrl+a d' to
detach from the screen session. You can now log out of the box ('ctrl+d').

Install and configure command line clients
------------------------------------------

To interact with and test your ZeroCloud deployment, you'll need to install a
handful of tools. You can install all of these tools from PyPI using ``pip``. 

From within your vagrant VM execute the following:

.. code-block:: bash

    $ sudo pip install python-swiftclient python-keystoneclient zpm

.. note::

    ``zpm`` (ZeroVM Package Manager) is a tool which make it easier to develop,
    package, and deploy applications for ZeroCloud.

To authenticate with your ZeroCloud installation, you'll need to set up your
credentials in some environment variables. A configuration file is provided
for convenience in ``$HOME/zerocloud/contrib/vagrant``.

.. code-block:: bash

    $ source /vagrant/adminrc

You can test your client configuration by running ``zpm auth``:

.. code-block:: bash

    $ zpm auth
    Auth token: PKIZ_Zrz_Qa5NJm44FWeF7Wp...
    Storage URL: http://127.0.0.1:8080/v1/AUTH_7fbcd8784f8843a180cf187bbb12e49c

Setting a couple of environment variables with these values will make commands
more concise and convenient to execute:

.. code-block:: bash

    $ export OS_AUTH_TOKEN=PKIZ_Zrz_Qa5NJm44FWeF7Wp...
    $ export OS_STORAGE_URL=http://127.0.0.1:8080/v1/AUTH_7fbcd8784f8843a180cf187bbb12e49c
