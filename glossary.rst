Glossary of Terms
=================

**Channel**
    Channels are the key component of the ZeroVM I/O subsystem. On the host
    system side, channels are backed by the file system using regular files,
    pipes, character devices, or TCP sockets. On the guest side, each channel
    is a device file, which can either be used as a character or block device.

    Channels are the only way for ZeroVM to communicate with the "outside
    world", i.e., the host file system, other ZeroVM nodes, etc. Before a
    ZeroVM instance starts, channels must be declared in the **Manifest**.

**Daemon mode**
    ZeroVM can be started in daemon mode to reduce startup of instances/nodes
    in a multi-node job. Although ZeroVM startup time is ~5ms, user programs,
    for example, running on **zpython**, will incur an additional startup
    penalty. Daemon mode allows a multi-node computation to "pre-warm" an
    instance and fork additional copies for each unit of computation, thereby
    paying the additional startup time penalty only once.

**Manifest**
    A text file which must be provided to ZeroVM in order to run a **NaCL**
    application. Manifest files must include the following *mandatory* fields:

    - ``Version``: Manifest format version.
    - ``Program``: Full path to a **NaCL** application to be validated and run.
    - ``Timeout``: Timeout, in seconds. ZeroVM will stop the user program and
      exit after the specified time has elapsed. Valid values are
      1..2147483647.
    - ``Memory``: Memory space in bytes available for the user program.
    - ``Channel``: Mapping for I/O between a ZeroVM instance and the host
      system. Multiple channels be specified in a manifest.

    Manifests can also contain the following *optional* fields:

    - ``Nameserver``: Address of a nameserver which resolves network channel
      definitions.
    - ``Node``: Node ID number of a given ZeroVM instance in a cluster of VMs.
      Manditory if ``NameServer`` is specified.
    - ``Job``: Path to a Unix socket. Used for receiving commands/manifests and
      to send reports in **Daemon mode**.

.. TODO(larsbutler): Add a more detailed `manifest` page and link it here.
   It would be nice to basically link to a detailed page containing all of
   this: https://github.com/zerovm/zerovm/blob/master/doc/manifest.txt


**NaCl (Native Client)**

    See http://en.wikipedia.org/wiki/Google_Native_Client.

**NVRAM (configuration file)**
    `INI-style <http://en.wikipedia.org/wiki/INI_file>`_ configuration file
    used by ZeroVM and the **ZRT**. Includes the following:

    - ``[fstab]`` section: Channel definitions for ``tar`` images to
      be mounted as directory/file hierarchies in the in-memory file system.
    - ``[env]`` section: Environment variable definitions.
    - ``[mapping]`` section: Channel definitions for stdin, stdout,
      stderr, and other devices not included in ``[fstab]``.
    - ``[debug]`` section: Optional. Debug verbosity level configuration.
    - ``[time]`` section: Optional. Defines the starting time for the ZeroVM
      clock. With this you can define the number of seconds since Jan 1, 1970.
      (See `Unix time <http://en.wikipedia.org/wiki/Unix_time>`_.)

.. TODO(larsbutler): Linked more detailed docs page here, with a full
   description of the NVRAM file and all of its fields.

**Trusted (code)**
    ZeroVM and the **ZRT**. Provides a secure sandbox for running **untrusted**
    code.

**Untrusted (code)**
    User code run inside the ZeroVM **NaCL**-based sandbox. Untrusted code is
    `validated <https://github.com/zerovm/validator>`_ before it is run.

.. TODO(larsbutler): This description needs expansion/improvement.

**zapp**
    ZeroVM Application. An archive file (typically created by **zpm**)
    containing a ``zapp.yml`` configuration file and user application code.

**ZeroCloud**
    Middleware for `OpenStack Swift <https://wiki.openstack.org/wiki/Swift>`_
    which provides the capability to run ZeroVM applications on object
    storage nodes. Can be used to initiate map/reduce-style jobs on collections
    of Swift objects.

    See https://github.com/zerovm/zerocloud.

**Zebra**
    Custom-configured deployment of **ZeroCloud**, hosted by `Rackspace
    <https://rackspace.com>`_. **Zebra** is an alpha-testing service and
    playground for **ZeroCloud**.

**zpm**
    ZeroVM Package Manager. Command-line utility which helps to create, bundle,
    deploy (to **ZeroCloud**), and execute (on **ZeroCloud**) ZeroVM user
    applications.

    See https://github.com/zerovm/zpm.

**zpython**
    **ZeroVM** ports of CPython interpreters. There are ongoing efforts to port
    both `Python 2.7.3 <https://github.com/zerovm/zpython2>`_ and
    `Python 3.2.2 <https://github.com/zerovm/zpython>`_ to run inside
    **ZeroVM**.

**ZRT**
    **ZeroVM** Runtime. Provides a POSIX-like environment and in-memory file
    system for use by **untrusted** user programs.

**zvsh**
    Utility program which makes ZeroVM easy to use by providing rich
    command-line options for running and debugging ZeroVM instances. Also
    includes manifest/NVRAM configuration file generation functionality (so you
    don't have to write all of your configuration files by hand).

    See https://github.com/zerovm/zerovm-cli.

**Zwift**
    Deprecated synonym for **ZeroCloud**.
