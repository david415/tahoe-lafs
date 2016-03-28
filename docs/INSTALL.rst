﻿.. -*- coding: utf-8-with-signature-unix; fill-column: 77 -*-

==================
Getting Tahoe-LAFS
==================

Welcome to `the Tahoe-LAFS project`_, a secure, decentralized, fault-tolerant
storage system. See `<about.rst>`_ for an overview of the architecture and
security properties of the system.

This procedure should work on Windows, Mac, OpenSolaris, and too many flavors
of Linux and of BSD to list.

.. _the Tahoe-LAFS project: https://tahoe-lafs.org

First: In Case Of Trouble
=========================

In some cases these instructions may fail due to peculiarities of your
platform.

If the following instructions don't Just Work without any further effort on
your part, then please write to `the tahoe-dev mailing list`_ where friendly
hackers will help you out.

.. _the tahoe-dev mailing list: https://tahoe-lafs.org/cgi-bin/mailman/listinfo/tahoe-dev

Pre-Packaged Versions
=====================

You may not need to build Tahoe at all.

If you are on Windows, please see `<windows.rst>`_ for platform-specific
instructions.

If you are on a Mac, you can either follow these instructions, or use the
pre-packaged bundle described in `<OS-X.rst>`_. The Tahoe project hosts
pre-compiled "wheels" for all dependencies, so use the ``--find-links=``
option described below to avoid needing a compiler.

Many Linux distributions include Tahoe-LAFS packages. Debian and Ubuntu users
can ``apt-get install tahoe-lafs``. See `OSPackages`_ for other
platforms.

.. _OSPackages: https://tahoe-lafs.org/trac/tahoe-lafs/wiki/OSPackages


Preliminaries
-------------

If you don't use a pre-packaged copy of Tahoe, you can build it yourself.
You'll need Python2.7, pip, and virtualenv. On unix-like platforms, you will
need a C compiler, the Python development headers, and some libraries
(libffi-dev and libssl-dev).

On a modern Debian/Ubuntu-derived distribution, this command will get you
everything you need::

    apt-get install build-essential python-dev libffi-dev libssl-dev python-virtualenv

On OS-X, install pip and virtualenv as described below. If you want to
compile the dependencies yourself (instead of using ``--find-links`` to take
advantage of the pre-compiled ones we host), you'll also need to install
Xcode and its command-line tools.

* python 2.7

Check if you already have an adequate version of Python installed by running
``python -V``. The latest version of Python v2.7 is required, which is 2.7.11
as of this writing. Python v2.6.x and v3 do not work. On Windows, we
recommend the use of native Python v2.7, not Cygwin Python. If you don't have
one of these versions of Python installed, `download`_ and install the latest
version of Python v2.7. Make sure that the path to the installation directory
has no spaces in it (e.g. on Windows, do not install Python in the "Program
Files" directory)::

    % python --version
    Python 2.7.11

.. _download: https://www.python.org/downloads/

* pip

Many Python installations already include ``pip``, but in case yours does
not, follow the instructions at https://pip.pypa.io/en/stable/installing/ ::

    % pip --version
    pip 8.1.1 from ... (python 2.7)

* virtualenv

Install ``virtualenv`` with the instructions at
https://virtualenv.pypa.io/en/latest/installation.html ::

    % virtualenv --version
    15.0.1

* C compiler and libraries

Except on OS-X, where the Tahoe project hosts pre-compiled wheels for all
dependencies, you will need several C libraries installed before you can
build. You will also need the Python development headers, and a C compiler
(your python installation should know how to find these).

On Debian/Ubuntu-derived systems, the necessary packages are ``python-dev``,
``libffi-dev``, and ``libssl-dev``, and can be installed with ``apt-get``. On
RPM-based system (like Fedora) these may be named ``python-devel``, etc,
instead, and cam be installed with ``yum`` or ``rpm``.

Install the Latest Tahoe-LAFS Release
------------------------------------

We recommend creating a fresh virtualenv for your Tahoe-LAFS install, to
isolate it from any python packages that are already installed (and to
isolate the rest of your system from Tahoe's dependencies).

This example uses a virtualenv named ``venv``, but you can call it anything
you like. Many people prefer to keep all their virtualenvs in one place, like
``~/.local/venvs/`` or ``~/venvs/``.

Use the virtualenv's ``pip`` to install the latest Tahoe-LAFS release from
PyPI with ``venv/bin/pip install tahoe-lafs``. After installation, run
``venv/bin/tahoe --version`` to confirm the install was successful::

 % virtualenv venv
 New python executable in ~/venv/bin/python2.7
 Installing setuptools, pip, wheel...done.
 % venv/bin/pip install tahoe-lafs
 Collecting tahoe-lafs
 ...
 Installing collected packages: ...
 Successfully installed ...
 % venv/bin/tahoe --version
 tahoe-lafs: 1.11.0
 foolscap: ...
 %

On OS-X, instead of ``pip install tahoe-lafs``, use this command to take
advantage of the hosted pre-compiled wheels::

 venv/bin/pip install --find-links=https://tahoe-lafs.org/deps tahoe-lafs


Install From a Source Tarball
-----------------------------

You can also download the source tarball first, unpack it, then install from
the unpacked source tree.

Download the latest stable release, `Tahoe-LAFS v1.11.0`_.

.. _Tahoe-LAFS v1.11.0: https://tahoe-lafs.org/source/tahoe-lafs/releases/tahoe-lafs-1.11.0.tar.bz2

Then unpack and install (again into a virtualenv)::

 % wget https://tahoe-lafs.org/source/tahoe-lafs/releases/tahoe-lafs-1.11.0.tar.bz2
 ...
 % tar xf tahoe-lafs-1.11.0.tar.bz2
 ...
 % cd tahoe-lafs-1.11.0
 % virtualenv venv
 New python executable in ~/tahoe-lafs-1.11.0/venv/bin/python2.7
 Installing setuptools, pip, wheel...done.
 % venv/bin/pip install .
 Processing ~/tahoe-lafs-1.11.0
 ...
 Installing collected packages: ...
 Successfully installed ...
 % venv/bin/tahoe --version
 tahoe-lafs: 1.11.0
 ...
 %


Hacking On Tahoe-LAFS
---------------------

To modify the Tahoe source code, you should get a git checkout, and install
with the ``--editable`` flag::

 % git clone https://github.com/tahoe-lafs/tahoe-lafs.git
 ...
 % cd tahoe-lafs
 % virtualenv venv
 New python executable in ~/tahoe-lafs/venv/bin/python2.7
 Installing setuptools, pip, wheel...done.
 % venv/bin/pip install --editable .
 Processing ~/tahoe-lafs-1.11.0
 ...
 Installing collected packages: ...
 Successfully installed ...
 % venv/bin/tahoe --version
 tahoe-lafs: 1.11.0
 ...
 %

This way, you won't have to re-run the ``pip install`` step each time you
modify the source code.

Running Tahoe-LAFS
------------------

The rest of the Tahoe-LAFS documentation assumes that you can run the
``tahoe`` executable that you just created. You have four basic options:

* Use the full path each time (e.g. ``~/venv/bin/tahoe``).
* "`Activate`_" the virtualenv with ``. venv/bin/activate``, to get a
  subshell with a ``$PATH`` that includes the ``venv/bin/`` directory, then
  you can just run ``tahoe``.
* Change your ``$PATH`` to include the ``venv/bin/`` directory, so you can
  just run ``tahoe``.
* Symlink from ``~/bin/tahoe`` to the ``tahoe`` executable. Since ``~/bin``
  is typically in your ``$PATH`` (at least if it exists when you log in),
  this will let you just run ``tahoe``.

You might also find the `pipsi`_ tool convenient: ``pipsi install
tahoe-lafs`` will create a new virtualenv, install tahoe into it, then
symlink just the executable (into ``~/.local/bin/tahoe``). Then either add
``~/.local/bin/`` to your ``$PATH``, or make one last symlink into
``~/bin/tahoe``.

.. _Activate: https://virtualenv.pypa.io/en/latest/userguide.html#activate-script
.. _pipsi: https://pypi.python.org/pypi/pipsi/0.9

Running the Self-Tests
----------------------

To run the self-tests from a source tree, you'll need ``tox`` installed. On a
Debian/Ubuntu system, use ``apt-get install tox``. You can also install it
into your tahoe-specific virtualenv with ``pip install tox``.

Then just run ``tox``. This will create a new fresh virtualenv, install Tahoe
(from the source tree, including any changes you have made) and all its
dependencies into the virtualenv, then run the unit tests. This ensures that
the tests are repeatable and match the results of other users, unaffected by
anything else installed on your machine. On a modern computer this will take
5-10 minutes, and should result in a "all tests passed" mesage::

 % tox
 GLOB sdist-make: ~/tahoe-lafs/setup.py
 py27 recreate: ~/tahoe-lafs/.tox/py27
 py27 inst: ~/tahoe-lafs/.tox/dist/tahoe-lafs-1.11.0a2.post8.dev0.zip
 py27 runtests: commands[0] | tahoe --version
 py27 runtests: commands[1] | trial --rterrors allmydata
 allmydata.test.test_auth
   AccountFileCheckerKeyTests
     test_authenticated ...                                           [OK]
     test_missing_signature ...                                       [OK]
  ...
 Ran 1186 tests in 423.179s
 
 PASSED (skips=7, expectedFailures=3, successes=1176)
 __________________________ summary ___________________________________
   py27: commands succeeded
   congratulations :) 

Common Problems
---------------

If you see an error like ``fatal error: Python.h: No such file or directory``
while compiling the dependencies, you need the Python development headers. If
you are on a Debian or Ubuntu system, you can install them with ``sudo
apt-get install python-dev``. On RedHat/Fedora, install ``python-devel``.

Similar errors about ``openssl/crypto.h`` indicate that you are missing the
OpenSSL development headers (``libssl-dev``). Likewise ``ffi.h`` means you
need ``libffi-dev``.


Run Tahoe-LAFS
--------------

Now you are ready to deploy a decentralized filesystem. The ``tahoe``
executable can configure and launch your Tahoe-LAFS nodes. See
`<running.rst>`_ for instructions on how to do that.
