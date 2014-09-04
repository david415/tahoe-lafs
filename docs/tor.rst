﻿.. -*- coding: utf-8-with-signature; fill-column: 77 -*-

=========================
Using Tahoe-LAFS with Tor
=========================

1.  `Use cases`_
2.  `Native Tor integration for Tahoe-LAFS`_
3.  `Software Dependencies`_
4.  `Configuration`_
5.  `Performance and security issues of Tor Hidden Services`_
6.  `Torsocks: the old way of configuring Tahoe-LAFS to use Tor`_

Use cases
=========

Tor is an anonymizing network used to help hide the identity of internet
clients and servers. Please see the Tor Project's website for more information:
https://www.torproject.org/


There are three potential use-cases for Tahoe-LAFS on the client side:

1. User does not care to protect their anonymity or to connect to anonymous
   storage servers. This document is not useful to you... so stop reading.

2. User does not care to protect their anonymity but they wish to connect to
   Tahoe-LAFS storage servers which are accessbile only via Tor Hidden Services.

3. User wishes to always use Tor to protect their anonymity when
   connecting to Tahoe-LAFS storage grids (whether or not the storage servers
   are Tor Hidden Services) [*].


For Tahoe-LAFS storage servers there are three use-cases:

1. Storage server operator does not care to protect their own anonymity 
   nor to help the clients protect theirs. Stop reading this document 
   and run your Tahoe-LAFS storage server using publicly routed TCP/IP.

2. The operator does not require anonymity for his storage server, but
   he wants it to be available over both publicly routed TCP/IP and
   through Tor Hidden Services. One possible reason to do this is
   because being reachable through Tor Hidden Services is a convenient
   way to bypass NAT or firewall that prevents publicly routed TCP/IP
   connections to your server. Another is that making your storage
   server reachable through Tor Hidden Services can provide better
   protection for your clients who themselves use Tor to protect their
   anonymity [*].

   See this Tor Project page for more information about Tor Hidden Services:
   https://www.torproject.org/docs/hidden-services.html.en

3. The operator wishes to protect their anonymity by making their 
   Tahoe server accessible only via Tor Hidden Services.



Native Tor integration for Tahoe-LAFS
=====================================

Native Tor integration for Tahoe-LAFS utilizes the Twisted endpoints API::
* https://twistedmatrix.com/documents/current/core/howto/endpoints.html

Twisted's endpoint parser plugin system is extensible via installing additional
Twisted packages. The native Tor integration for Tahoe-LAFS uses 
endpoint and parser plugins from the txsocksx and txtorcon modules.
Although the Twisted endpoint API is very flexible it is missing a feature so that
servers can be written in an endpoint agnostic style. We've opened a Twisted trac
ticket for this feature here::
* https://twistedmatrix.com/trac/ticket/7603

Once this ticket is resolved then an additional changes can be made to Foolscap
so that it's server side API is completely endpoint agnostic which will allow
users to easily to use Tahoe-LAFS with many protocols on the server side.

txsocksx will try to use the system tor's SOCKS port if available;
attempts are made on ports 9050 and 9151. Currently the maintainer of txsocksx
has not merged in our code for the Tor client endpoint. We'll use
this branch until the Tor endpoint code is merged upstream::
* https://github.com/david415/txsocksx/tree/endpoint_parsers_retry_socks

txtorcon will use the system tor control port to configure Tor Hidden Services
pending resolution of tor trac ticket 11291::
* https://trac.torproject.org/projects/tor/ticket/11291

See also Tahoe-LAFS Tor related tickets #1010 and #517.



Software Dependencies
=====================

* Tor (tor) must be installed. See here:
  https://www.torproject.org/docs/installguide.html.en

* The "Tor-friendly" branch of txsocksx must be installed
  ( Once this is merged then you can use upstream txsocksx;
  https://github.com/habnabit/txsocksx/pull/8 ) ::

   pip install git+https://github.com/david415/txsocksx.git

* txtorcon must be installed ::

   pip install txtorcon

Once these software dependencies are installed and the Tahoe-LAFS node
is restarted, then no further configuration is necessary for "unsafe"
Tor connectivity to other Tahoe-LAFS nodes (client use-case 2 from `Use cases`_, above).

In order to implement client use-case 3 or server use-cases 2 or 3, further
configuration is necessary.


Configuration
=============

``[node]``
``anonymize = (boolean, optional)``

This specifies two changes in behavior:
  1. Transform all non-Tor client endpoints into Tor client endpoints.
  2. Force ``tub.location`` to be set to "safe" values.

This option is **critical** to preserving the client's anonymity (client
use-case 3 from `Use cases`_, above). It is also necessary to
preserve a server's anonymity (server use-case 3).

When ``anonymize`` is set to ``true`` then ``tub.location`` does not need
to be specified... and it is an error to specify a ``tub.location`` value
that contains anything other than "UNREACHABLE" or a Tor Hidden Service
Twisted endpoint descriptor string.

If server use-case 2 from `Use cases`_ above is desired then you can set
``tub.location`` to a Tor Hidden Service endpoint string AND "AUTODETECT"
like this::
  tub.location = "AUTODETECT,onion:80:hiddenServiceDir=/var/lib/tor/my_service"

It is an error to specify a ``tub.location`` value that contains "AUTODETECT"
when ``anonymize`` is also set to ``true``.

Operators of Tahoe-LAFS storage servers wishing to protect the identity of their
storage server should set ``anonymize`` to ``true`` and specify a
Tor Hidden Service endpoint descriptor string for the ``tub.location``
value in the ``tahoe.cfg`` like this::
   tub.location = "onion:80:hiddenServiceDir=/var/lib/tor/my_service"

Setting this configuration option is necessary for Server use-cases 2 and 3
(from `Use cases`_, above).


Performance and security issues of Tor Hidden Services
======================================================

If you are running a server which does not itself need to be
anonymous, should you make it reachable as a Tor Hidden Service or
not? Or should you make it reachable *both* as a Tor Hidden Service
and as a publicly traceable TCP/IP server?

There are several trade-offs effected by this decision.

NAT/Firewall penetration
------------------------

Making a server be reachable as a Tor Hidden Service makes it
reachable even if there are NATs or firewalls preventing direct TCP/IP
connections to the server.

Anonymity
---------

Making a Tahoe-LAFS server accessible *only* via Tor Hidden Services
can be used to guarantee that the Tahoe-LAFS clients use Tor to
connect. This prevents misconfigured clients from accidentally
de-anonymizing themselves by connecting to your server through the
traceable Internet.

Also, interaction, through Tor, with a Tor Hidden Service may be more
protected from network traffic analysis than interaction, through Tor,
with a publicly traceable TCP/IP server.

**XXX is there a document maintained by Tor developers which substantiates or refutes this belief?
If so we need to link to it. If not, then maybe we should explain more here why we think this?**

Performance
-----------

A client connecting to a Tahoe-LAFS server through Tor incurs
substantially higher latency and sometimes worse throughput than the
same client connecting to the same server over a normal traceable
TCP/IP connection.

A client connecting to a Tahoe-LAFS server which is a Tor Hidden
Service incurs much more latency and probably worse throughput.

Positive and negative effects on other Tor users
------------------------------------------------

Sending your Tahoe-LAFS traffic over Tor adds cover traffic for other
Tor users who are also transmitting bulk data. So that is good for
them -- increasing their anonymity.

However, it makes the performance of other Tor users' interactive
sessions -- e.g. ssh sessions -- much worse. This is because Tor
doesn't currently have any prioritization or quality-of-service
features, so someone else's ssh keystrokes may have to wait in line
while your bulk file contents get transmitted. The added delay might
make other people's interactive sessions unusable.

Both of these effects are doubled if you upload or download files to a
Tor Hidden Service, as compared to if you upload or download files
over Tor to a publicly traceable TCP/IP server.



Torsocks: the old way of configuring Tahoe-LAFS to use Tor
==========================================================

Before the native Tor integration for Tahoe-LAFS, users would use Torsocks.
Please see these pages for more information about Torsocks::
* https://code.google.com/p/torsocks/
* https://trac.torproject.org/projects/tor/wiki/doc/torsocks
* https://github.com/dgoulet/torsocks/


Starting And Stopping
---------------------

Assuming you have your Tahoe-LAFS node directory placed in **~/.tahoe**,
use Torsocks to start Tahoe like this::
   usewithtor tahoe start

Likewise if restarting, then with Torsocks like this::
   usewithtor tahoe restart

After Tahoe is started, additional Tahoe commandline commands will not
need to be executed with Torsocks because the Tahoe gateway long running
process handles all the network connectivity.


Configuration
-------------

Before Tahoe-LAFS had native Tor integration it would deanonymize the user if a
``tub.location`` value is not set. This is because Tahoe-LAFS at that time
defaulted to autodetecting the external IP interface and announced that IP
address to the server.


**Tahoe-LAFS + Torsocks client configuration**

Run a node using ``torsocks``, in client-only mode (i.e. we can
make outbound connections, but other nodes will not be able to connect
to us). The literal '``client.fakelocation``' will not resolve, but will
serve as a reminder to human observers that this node cannot be reached.
"Don't call us.. we'll call you"::

    tub.port = 8098
    tub.location = client.fakelocation:0


**Tahoe-LAFS + Torsocks storage server configuration**

Run a node behind a Tor proxy, and make the server available as a Tor
"hidden service". (This assumes that other clients are running their
node with ``torsocks``, such that they are prepared to connect to a
``.onion`` address.) The hidden service must first be configured in
Tor, by giving it a local port number and then obtaining a ``.onion``
name, using something in the ``torrc`` file like::

  HiddenServiceDir /var/lib/tor/hidden_services/tahoe
  HiddenServicePort 29212 127.0.0.1:8098

once Tor is restarted, the ``.onion`` hostname will be in
``/var/lib/tor/hidden_services/tahoe/hostname``. Then set up your
``tahoe.cfg`` like::

  tub.port = 8098
  tub.location = ualhejtq2p7ohfbb.onion:29212
