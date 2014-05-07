
from twisted.internet import address
from foolscap.api import Violation, RemoteException, DeadReferenceError, \
     SturdyRef

import re

# TODO: set this from tahoe.cfg? or something less ugly...
only_tor = True

CONVERT_ENDPOINT_RE=re.compile(r"^[^:]+:(.+)")

def get_host_from_endpoint(endpointDesc):
    mo = CONVERT_ENDPOINT_RE.search(endpointDesc)
    if mo:
        vars = mo.group(1).split(':')
        host = vars[0]
        if '=' in host:
            for var in vars:
                # BUG: check for error
                key, value = var.split('=')
                if key == 'host':
                    return value
        else:
            return host
    else:
        raise ValueError("failed to parse twisted endpoint descriptor")


def add_version_to_remote_reference(rref, default):
    """I try to add a .version attribute to the given RemoteReference. I call
    the remote get_version() method to learn its version. I'll add the
    default value if the remote side doesn't appear to have a get_version()
    method."""
    d = rref.callRemote("get_version")
    def _got_version(version):
        rref.version = version
        return rref
    def _no_get_version(f):
        f.trap(Violation, RemoteException)
        rref.version = default
        return rref
    d.addCallbacks(_got_version, _no_get_version)
    return d

def trap_and_discard(f, *errorTypes):
    f.trap(*errorTypes)
    pass

def trap_deadref(f):
    return trap_and_discard(f, DeadReferenceError)


def hosts_for_rref(rref, ignore_localhost=True):
    # actually, this only returns hostnames
    advertised = []
    for hint in rref.getLocationHints():
        assert isinstance(hint, str)
        host = get_host_from_endpoint(hint)
        if ignore_localhost and host == "127.0.0.1":
            continue
        advertised.append(host)
    return advertised

def hosts_for_furl(furl, ignore_localhost=True):
    advertised = []
    for hint in SturdyRef(furl).locationHints:
        assert isinstance(hint, str)
        host = get_host_from_endpoint(hint)
        if ignore_localhost and host == "127.0.0.1":
            continue
        advertised.append(host)

    return advertised

def stringify_remote_address(rref):
    remote = rref.getPeer()
    if isinstance(remote, address.IPv4Address):
        return "%s:%d" % (remote.host, remote.port)
    # loopback is a non-IPv4Address
    return str(remote)
