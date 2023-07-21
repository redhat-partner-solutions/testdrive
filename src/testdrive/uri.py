### SPDX-License-Identifier: GPL-2.0-or-later

"""Test URIs"""

from urllib.parse import (
    urlsplit,
    urlunsplit,
    urlencode,
    quote_plus,
)

class UriBuilder:
    """A builder of URIs relative to a `base` absolute URI"""
    def __init__(self, base, **kwargs):
        (scheme, authority, path, query, fragment) = urlsplit(base)
        if not scheme or query or fragment or base.endswith('#'):
            raise ValueError(base)
        self._path_sep = ':' if scheme.lower() == 'urn' else '/'
        head = path.split(self._path_sep)
        if head[-1] == '':
            head = head[:-1]
        self._scheme = scheme
        self._authority = authority
        self._head = head
        self._query = urlencode(kwargs, quote_via=quote_plus) if kwargs else None
    def build(self, path):
        """Build a URI from `path` relative to this instance's base"""
        tail = path.split('/')
        if tail[0] == '':
            tail = tail[1:]
        tail.append('')
        return urlunsplit((
            self._scheme,
            self._authority,
            self._path_sep.join(self._head + tail),
            self._query,
            None, # never supply a fragment
        ))
