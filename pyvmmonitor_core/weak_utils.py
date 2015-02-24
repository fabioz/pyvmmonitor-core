# License: LGPL
#
# Copyright: Brainwy Software

import weakref
_NONE_LAMDA = lambda: None


def get_weakref(obj):
    if obj is None:
        return _NONE_LAMDA

    if isinstance(obj, weakref.ref):
        return obj

    return weakref.ref(obj)


def assert_weakref_none(ref):
    r = ref()
    if r is None:
        return
    r = None

    import sys

    sys.exc_clear()
    r = ref()
    if r is None:
        return

    r = ref()
    assert r is not None


class WeakList(object):

    def __init__(self, lst=None):
        self._items = []
        if lst is not None:
            for obj in lst:
                self.append(obj)

    def append(self, obj):
        # Add backwards to ease on iteration removal (on our __iter__ we'll go the other way
        # around so that the client sees it in the proper order).
        self._items.insert(0, weakref.ref(obj))

    def remove(self, obj):
        i = len(self._items) - 1
        while i >= 0:
            ref = self._items[i]
            d = ref()
            if d is None or d is obj:
                del self._items[i]
            i -= 1

    def __iter__(self):
        i = len(self._items) - 1
        while i >= 0:
            ref = self._items[i]
            d = ref()
            if d is None:
                del self._items[i]
            else:
                yield d
            i -= 1

    def iter_refs(self):
        return iter(reversed(self._items))

    def clear(self):
        del self._items[:]
