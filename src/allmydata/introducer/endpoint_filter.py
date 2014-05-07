

import re
from foolscap.referenceable import decode_furl

CONVERT_ENDPOINT_RE=re.compile(r"^[^:]+:(.+)")

# XXX - sloppy poppy?
def furl_to_tor(furl):
    furl_tuple = decode_furl(furl)
    tor_furl   = encode_as_tor_furl(*furl_tuple)
    return tor_furl

def encode_as_tor_furl(encrypted, tubID, location_hints, name):
    location_hints_s = ",".join(map(convert_to_tor_endpoint, location_hints))
    if encrypted:
        return "pb://" + tubID + "@" + location_hints_s + "/" + name
    else:
        # XXX
        return "pbu://" + convert_to_tor_endpoint(location_hints) + "/" + name

def convert_to_tor_endpoint(endpointDesc):
    mo = CONVERT_ENDPOINT_RE.search(endpointDesc)
    if mo:
        return "tor:" + mo.group(1)
    else:
        raise ValueError("failed to parse twisted endpoint descriptor")
