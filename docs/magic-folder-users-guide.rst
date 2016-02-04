
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

This command has the side-effect of creating an alias called
"magic" which is a link to a Tahoe-LAFS cryptographic capability.
Whoever possesses this capability can act as Magic-Folder group admin
and invite additional users to the group.

She can then invite herself ::

  tahoe magic-folder invite Alice

This invite command results in an invite-code being printed to stdout.
Alice uses this invite code to join the group::

  tahoe magic-folder join <INVITE-CODE>

Or Alice can create, invite herself and join in one command::

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

scope
`````

The security and design tradeoffs we discuss in this section only refer
to the current version of Magic-Folder. Let it be know that future versions
may well have vastly different security properties as our development efforts
continue to shed light onto the mysteries of capability and security domain
isolation analysis for decentralized ciphertext storage systems.


context
```````

The current version of Magic-Folder only supports correct conflict
detection for two concurrent clients, therefore it only makes sense
to have concurrent groups of two.

The Tahoe-LAFS design for decentralized ciphertext storage makes very
simple use of the grid storage servers. The client depends on the storage
servers for very simple behavior serving requested shares of ciphertext.

Tahoe-LAFS does not posses any access control ablities. If a client has
access to a given Tahoe-LAFS grid then nothing can prevent that client from
retreiving the plaintext provided that the client possess a valid cryptographic
capability which allows for retrieval AND decryption of the ciphertext.


tradeoffs
`````````

The current CLI design and data model have created a single point of failure
(SPOF), the admin. It is remarkable that the admin not only cause data loss
but also imporsonate other users.

Clients do not record full file history, therefore data loss can be caused when
a file deletion causes the Tahoe-LAFS cryptographic capability from being
preserved. When a client removes a file the rest of the group members also cooperatively
remove and forget their crypgraphic capability for that file. It it noteworthy that
an actor in the Magic-Folder group could choose to remember the historical
cryptographic capabilities. For this case revocation is not possible because
the storage servers will continue to serve the ciphertext if asked for the valid
share id.
