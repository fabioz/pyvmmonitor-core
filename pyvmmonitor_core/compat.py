'''
License: LGPL

Copyright: Brainwy Software

Helpers to deal with python2/3.
'''

import sys

PY2 = sys.version_info[0] < 3
PY3 = not PY2


if PY3:
    unicode = str
    bytes = bytes
    xrange = range
    izip = zip
    from io import StringIO

    def iterkeys(d):
        return d.keys()

    def itervalues(d):
        return d.values()

    def iteritems(d):
        return d.items()

    def values(d):
        return list(d.values())

    def keys(d):
        return list(d.keys())

    def items(d):
        return list(d.items())

    def as_bytes(b):
        if b.__class__ == str:
            return b.encode('utf-8')
        return b

    def as_bytesf(b):
        if b.__class__ == str:
            return b.encode(sys.getfilesystemencoding())
        return b

    def as_unicode(b):
        if b.__class__ != str:
            return b.decode('utf-8', 'replace')
        return b

    def as_unicodef(b):  # unicode filesystem
        if b.__class__ != str:
            return b.decode(sys.getfilesystemencoding(), 'replace')
        return b

    def next(it):
        return it.__next__()


else:
    unicode = unicode
    bytes = str
    xrange = xrange
    import itertools
    izip = itertools.izip

    from StringIO import StringIO

    def as_bytes(b):
        if b.__class__ == unicode:
            return b.encode('utf-8')
        return b

    def as_bytesf(b):
        if b.__class__ == unicode:
            return b.encode(sys.getfilesystemencoding())
        return b

    def as_unicode(b):
        if b.__class__ != unicode:
            return b.decode('utf-8', 'replace')
        return b

    def as_unicodef(b):  # unicode filesystem
        if b.__class__ != unicode:
            return b.decode(sys.getfilesystemencoding(), 'replace')
        return b

    def iterkeys(d):
        return d.iterkeys()

    def itervalues(d):
        return d.itervalues()

    def iteritems(d):
        return d.iteritems()

    def values(d):
        return d.values()

    def keys(d):
        return d.keys()

    def items(d):
        return d.items()

    def next(it):
        return it.next()
