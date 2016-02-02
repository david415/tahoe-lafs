
=========================
Magic Folder User's Guide
=========================

1.  `This document`_
2.  `Preparation`_
2.  `Security properties`_


This document
=============

This is documentation for helping users to set up a
Tahoe-LAFS client node configured to use Magic-Folder.
We will explain how to use Magic-Folder groups as a user
and as an admin. However Magic-Folder may in the future
change the CLI tools and data-model which would alter
many of the security properties, some of which are expressed
as design tradeoffs between data durability and data revocation.


Preparation
===========

The admins and users of a Magic-Folder group must have
access to an existing Tahoe-LAFS storage grid. As per usual
their tahoe configuration must specify the appropriate
introducer FURL(s) and or storage server connection information.


Setting up Magic Folder
=======================

Alice creates a new Magic-Folder. ::

  tahoe magic-folder create magic:


She can then invite herself and then join as separate subsequent steps
or she can create, invite herself and join in one command::

  tahoe magic-folder create magic: alice alice-magic-folder


Alice can invite Bob::

  tahoe magic-folder invite magic: bob


This invite command prints out an invite-code which Alice
must transmit to Bob with an existing confidential communications channel
such as OTR chat or PGP e-mail.

Bob joins Alice's Magic-Folder::

  tahoe magic-folder join "$INVITECODE" bob-magic-folder



Security properties
===================

The security and design tradeoffs we discuss in this section only refer
to the current version of Magic-Folder. Let it be know that future versions
may well have vastly different security properties as our development efforts
continue to shed light onto the mysteries of capability and security domain
isolation analysis for distributed ciphertext storage systems.

The current version of Magic-Folder only supports correct conflict
detection for two concurrent clients, however it's worth noting
that the current design allows the admin to impersonate the user.

Furthermore this current design has some data revocation properties but relatively
weak data durability properties. To give some more context to this design and
security analysis I'll first explain a bit about how to analyze the security properties
of using Tahoe-LAFS without Magic-Folder.


security tradeoffs for Tahoe-LAFS without Magic-Folder
------------------------------------------------------

The current Tahoe-LAFS system right now has a very different set of
security tradeoffs than most ciphertext storage systems, namely that
there is no access control at all. Rather than utilizing centralized
pockets of excess authority, access control lists, Tahoe implements
a cryptographic capabilties security model which is a cryptographic
interpretation of the object capability security model.

For a good introduction to the object security capability model we
recommend reading "The Structure of Authority" [1] by Mark S. Miller.

Our Tahoe-LAFS cryptographic capabilities are granular references to
not only address remote file objects but to decrypt them as well. Therefore
this allows granular condifential sharing of file objects between any
of the users who have connecting information for that Tahoe storage grid.

Users will share these cryptographic capabilities but they must use
cryptographic channels to share them otherwise their capabilities will
be leaked on the network and there could be systems administrators
who would find and use these caps.

Tahoe-LAFS currently does not have file deletion for immutable file objects,
although there is a ciphertext garbage collector which can optionally run if the
Tahoe storage operator enables it. If a user accidentally leaks his
capability to an e-mailing list the capability will be irrevocably
leaked. If someone gains access to the storage grid then that leaked
capability will give them access to the plaintext documents. There is
no convenient way to recover from this situation. If the storage servers
garbage collect the ciphertext for the leaked file object then they
will stop serving the ciphertext.


analysis of security domain isolation
`````````````````````````````````````

The confidentiality of the user's ciphertext which is stored
on Tahoe-LAFS storage nodes depends on the security isolation
of the user's endpoint device which runs the Tahoe-LAFS client node.
For the purposes of describing attack surface are on the confidentiality
of the data we consider that the user's Tahoe-LAFS client node is
effectively in the same security domain as the ciphertext.





security tradeoffs for Tahoe-LAFS with current Magic-Folder
-----------------------------------------------------------


