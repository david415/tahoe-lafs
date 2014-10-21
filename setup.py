#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys; assert sys.version_info < (3,), ur"Tahoe-LAFS does not run under Python 3. Please use a version of Python between 2.6 and 2.7.x inclusive."

# Tahoe-LAFS -- secure, distributed storage grid
#
# Copyright © 2006-2012 The Tahoe-LAFS Software Foundation
#
# This file is part of Tahoe-LAFS.
#
# See the docs/about.rst file for licensing information.

import os, subprocess, shutil
from setuptools import setup
from setuptools import Command

trove_classifiers=[
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Environment :: Web Environment",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "License :: DFSG approved",
    "License :: Other/Proprietary License",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: System Administrators",
    "Operating System :: Microsoft",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: Microsoft :: Windows :: Windows NT/2000",
    "Operating System :: Unix",
    "Operating System :: POSIX :: Linux",
    "Operating System :: POSIX",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: OS Independent",
    "Natural Language :: English",
    "Programming Language :: C",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.4",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Topic :: Utilities",
    "Topic :: System :: Systems Administration",
    "Topic :: System :: Filesystems",
    "Topic :: System :: Distributed Computing",
    "Topic :: Software Development :: Libraries",
    "Topic :: Communications :: Usenet News",
    "Topic :: System :: Archiving :: Backup",
    "Topic :: System :: Archiving :: Mirroring",
    "Topic :: System :: Archiving",
    ]

def run_command(args, cwd=None, verbose=False):
    print "running '%s'" % " ".join(args)
    try:
        # remember shell=False, so use e.g. git.cmd on windows, not just git
        p = subprocess.Popen(args, cwd=cwd)
    except EnvironmentError, e:
        if verbose:
            print "unable to run %s" % args[0]
            print e
        return False
    p.communicate()
    if p.returncode != 0:
        if verbose:
            print "unable to run %s (error)" % args[0]
        return False
    return True


class Trial(Command):
    description = "run trial (use 'bin%stahoe debug trial' for the full set of trial options)" % (os.sep,)
    # This is just a subset of the most useful options, for compatibility.
    user_options = [ ("no-rterrors", None, "Don't print out tracebacks as they occur."),
                     ("rterrors", "e", "Print out tracebacks as they occur (default, so ignored)."),
                     ("until-failure", "u", "Repeat a test (specified by -s) until it fails."),
                     ("reporter=", None, "The reporter to use for this test run."),
                     ("suite=", "s", "Specify the test suite."),
                     ("quiet", None, "Don't display version numbers and paths of Tahoe dependencies."),
                   ]

    def initialize_options(self):
        self.rterrors = False
        self.no_rterrors = False
        self.until_failure = False
        self.reporter = None
        self.suite = "allmydata"
        self.quiet = False

    def finalize_options(self):
        pass

    def run(self):
        args = [sys.executable, os.path.join('bin', 'tahoe')]
        if not self.quiet:
            args.append('--version-and-path')
        args += ['debug', 'trial']
        if self.rterrors and self.no_rterrors:
            raise AssertionError("--rterrors and --no-rterrors conflict.")
        if not self.no_rterrors:
            args.append('--rterrors')
        if self.until_failure:
            args.append('--until-failure')
        if self.reporter:
            args.append('--reporter=' + self.reporter)
        if self.suite:
            args.append(self.suite)
        rc = subprocess.call(args)
        sys.exit(rc)




class SafeDevelop(Command):
    description = "safely install everything into a local virtualenv"
    user_options = []

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass

    def run(self):
        if os.path.exists("venv"):
            shutil.rmtree("venv") # clobber it
        # or add 'support' to sys.path, import virtualenv, munge sys.argv,
        # virtualenv.main(), replace sys.argv
        cmd = [sys.executable, "support/virtualenv.py", "venv"]
        if not run_command(cmd):
            print "error while creating virtualenv in ./venv"
            sys.exit(1)
        print "venv created"
        # or import support/peep.py, run peep.commands["install"](args)
        cmd = ["venv/bin/python", "support/peep.py",
               "install",
               "--download-cache", "../tahoe-dep-cache",
               "-r", "requirements.txt"]
        if not run_command(cmd):
            print "error while installing dependencies"
            sys.exit(1)
        cmd = ["venv/bin/python", "setup.py", "develop"]
        if not run_command(cmd):
            print "error while installing dependencies"
            sys.exit(1)
        print "dependencies and tahoe installed into venv"
        print "Now use './bin/tahoe' to create and launch a node."

setup(name="tahoe",
      version = "0.0.666",
      description='secure, decentralized, fault-tolerant filesystem',
      long_description=open('README.txt', 'rU').read(),
      author='the Tahoe-LAFS project',
      author_email='tahoe-dev@tahoe-lafs.org',
      url='https://tahoe-lafs.org/',
      license='GNU GPL', # see README.txt -- there is an alternative licence
      cmdclass={"trial": Trial,
                "safe_develop": SafeDevelop,
                },
      package_dir = {'':'src'},
      packages=['allmydata',
                'allmydata.frontends',
                'allmydata.immutable',
                'allmydata.immutable.downloader',
                'allmydata.introducer',
                'allmydata.mutable',
                'allmydata.scripts',
                'allmydata.storage',
                'allmydata.test',
                'allmydata.util',
                'allmydata.web',
                'allmydata.windows',
                'buildtest'],
      install_requires=[
          "zfec==1.4.24",
          "simplejson==3.5.3",
          "Twisted==14.0.0",
          "foolscap==0.6.4",
          "pyOpenSSL==0.14",
          "Nevow==0.11.1",
          "mock==1.0.1",
          "pycryptopp==0.6.0.1206569328141510525648634803928199668821045408958",
          # twisted.conch needs these, but does not declare them
          "pycrypto==2.6.1",
          "pyasn1==0.1.7",
          ],
      classifiers=trove_classifiers,
      test_suite="allmydata.test",
      package_data={"allmydata.web": ["*.xhtml",
                                      "static/*.js", "static/*.png", "static/*.css",
                                      "static/img/*.png",
                                      "static/css/*.css",
                                      ]
                    },
      entry_points = { 'console_scripts': [ 'tahoe = allmydata.scripts.runner:run' ] },
      )
