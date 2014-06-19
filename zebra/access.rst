.. _access:

Accessing Zebra
===============


Requesting an Invite Code
-------------------------

The Zebra playground was created to support and grow the ZeroVM community.
Eventually we would like to make Zebra open to any and all members of the ZeroVM
community interested in experimenting with the technology and testing new
features at scale on real hardware. Unfortunately, due to the small team
supporting Zebra, and the fact that we are still stabilizing the code, we are
currently only allowing a limited number of community members access to the
environment.

If you are interested in getting access to Zebra to begin experimenting with the
ZeroVM you must first request an invite code. You can request an invite code by
emailing: zebra-requests@zerovm.org.  Please include your name and a brief
description of the use case that you would like to experiment with on Zebra.
We began sending invite codes out in May of 2014 and will continue to send
invite codes to community members as we work towards a more automated way of 
controlling access to Zebra. 

Creating an Account on Zebra
-------------------------------

Once you have an invite code (see above) you can follow these steps to create an
account on Zebra.  Keep in mind that because Zebra is integrated with Google
authentication you must have a Google account (a gmail account works) in order
to create an account on Zebra.

#. Navigate to the Zebra registration page:
   https://zebra.zerovm.org/register.html
#. Please read the disclaimer to understand the risks associated with using
   Zebra.
#. On the bottom of the page enter your invite code.
#. Click on the button that says "Register with your Google Account".
#. You will be prompted to login to your Google account and authorize Zebra to
   access your basic Google account info.
#. Next, navigate to the main Zebra page: https://zebra.zerovm.org
#. Now click on "Login with Google" button on the bottom of the page.
#. Your "tenant", "X Auth User", and "X Auth Key" will be automatically 
   populated.
#. Your account is now fully created and setup on Zebra.
#. Next, if you click login you will be able to start using the ZeroVM File
   Manager to access Zebra.
#. If you forget your X Auth Key, or if you logout and need to log back in, you
   can always click the "Login with Google" button again, and it will re-populate
   your account details.
#. You can also take your credentials from the Zebra login page to setup CLI
   tools to access Zebra.

Interacting with Zebra
----------------------

Once you have created an account on Zebra there are a couple of different ways
to interact with the playground.

The first is to use the web-based graphical user interface called the ZeroVM
File Manager. If you have an account on Zebra you can access the `ZeroVM File
Manager <https://zebra.zerovm.org>`_ online.

In addition to the File Manager, there are a variety of Command Line Tools
(CLIs) that can be used to interact with Zebra. You can find documentation on
the :ref:`clitools` in another section of this site.

Finally, you can also interact directly with the Zebra API via HTTP using a tool
such as cURL. This type of interaction is beyond the scope of this documentation.

