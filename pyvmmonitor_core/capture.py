# License: LGPL
#
# Copyright: Brainwy Software

'''
Helper to capture streams (stdout, stderr).

Sample uses:

with capture('stderr') as stderr:
    ...

print(stderr.getvalue())


with capture(('stderr', 'stdout')) as streams:
    ...

print(streams.getvalue())

'''
from __future__ import with_statement
import sys

PY2 = sys.version_info[0] < 3
PY3 = not PY2


def capture(streams=('stdout', 'stderr'), keep_original=False):
    if not isinstance(streams, (list, tuple)):
        streams = (streams,)
    return _RedirectionScope(keep_original, streams)


# ==================================================================================================
# Private API
# ==================================================================================================
class _StreamRedirector:

    def __init__(self, *args):
        self._streams = args

    def write(self, s):
        for r in self._streams:
            try:
                r.write(s)
            except:
                pass

    def isatty(self):
        return False

    def flush(self):
        for r in self._streams:
            r.flush()

    def __getattr__(self, name):
        for r in self._streams:
            if hasattr(r, name):
                return r.__getattribute__(name)
        raise AttributeError(name)


class _DummyStream:

    def __init__(self):
        self.buflist = []
        import os
        self.encoding = os.environ.get('PYTHONIOENCODING', 'utf-8')

    def getvalue(self):
        return ''.join(self.buflist)

    def write(self, s):
        if not PY3:
            if isinstance(s, unicode):
                s = s.encode(self.encoding)
        self.buflist.append(s)

    def isatty(self):
        return False

    def flush(self):
        pass


class _RedirectionScope(object):

    def __init__(self, keep_original, streams):
        self.keep_original = keep_original
        self.streams = streams
        self.original_streams = []

    def __enter__(self, *args, **kwargs):
        stream = _DummyStream()

        for std in self.streams:
            original = getattr(sys, std)
            self.original_streams.append(original)

            if self.keep_original:
                setattr(sys, std, _StreamRedirector(original, stream))
            else:
                setattr(sys, std, stream)
        return stream

    def __exit__(self, *args, **kwargs):
        for std, original in zip(self.streams, self.original_streams):
            setattr(sys, std, original)
