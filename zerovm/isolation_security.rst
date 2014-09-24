.. _zerovm-isolation-security:

Isolation and Security
======================

ZeroVM has two key security components: static binary validation and a limited
system call API.

Static binary validation works by ensuring that untrusted code does not execute
any unsafe instructions. All jumps must target "the start of 32-byte-aligned blocks,
and instructions are not allowed to straddle these blocks". (See
http://en.wikipedia.org/wiki/Google_Native_Client and
http://research.google.com/pubs/pub34913.html.) The big advantage of this is
that validation can be performed just once before executing the untrusted
program, and no further validation or interpretation is required. All of this
is provided by
`Native Client <http://en.wikipedia.org/wiki/Google_Native_Client>`_ and is not
unique to ZeroVM.

The second security component--a limited syscall API--is a major differentiator
between plain NaCl and ZeroVM. In ZeroVM, only six system calls are available:

    - ``pread``
    - ``pwrite``
    - ``jail``
    - ``unjail``
    - ``fork``
    - ``exit``

This minimizes potential attack surfaces and facilitates security audits of the
core isolation mechanisms. Compare this to the standard
`NaCl system calls <https://code.google.com/p/nativeclient/wiki/SystemCalls>`_,
of which there are more than 50.
