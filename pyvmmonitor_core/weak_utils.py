# License: LGPL
#
# Copyright: Brainwy Software

import inspect
import weakref

from pyvmmonitor_core.ordered_set import OrderedSet
from pyvmmonitor_core.weakmethod import WeakMethod


_NONE_LAMDA = lambda: None


def get_weakref(obj):
    if obj is None:
        return _NONE_LAMDA

    if isinstance(obj, weakref.ref):
        return obj

    if inspect.ismethod(obj):
        return WeakMethod(obj)

    return weakref.ref(obj)


def assert_weakref_none(ref):
    r = ref()
    if r is None:
        return
    r = None

    import sys

    if hasattr(sys, 'exc_clear'):
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

    def __len__(self):
        i = 0
        for _k in self:
            i += 1
        return i


class WeakSet(object):

    def __init__(self):
        self._items = set()

    def add(self, item):
        self._items.add(get_weakref(item))

    def remove(self, item):
        self._items.remove(get_weakref(item))

    def discard(self, item):
        try:
            self.remove(item)
        except KeyError:
            pass

    def clear(self):
        self._items.clear()

    def __iter__(self):
        for ref in self._items.copy():
            d = ref()
            if d is None:
                self._items.remove(ref)
            else:
                yield d

    def __len__(self):
        i = 0
        for _k in self:
            i += 1
        return i


class WeakOrderedSet(object):

    def __init__(self):
        self._items = OrderedSet()

    def add(self, item):
        self._items.add(get_weakref(item))

    def remove(self, item):
        self._items.remove(get_weakref(item))

    def discard(self, item):
        self._items.discard(get_weakref(item))

    def clear(self):
        self._items.clear()

    def __iter__(self):
        for ref in list(self._items):
            d = ref()
            if d is None:
                self._items.discard(ref)
            else:
                yield d

    def __len__(self):
        i = 0
        for _k in self:
            i += 1
        return i
