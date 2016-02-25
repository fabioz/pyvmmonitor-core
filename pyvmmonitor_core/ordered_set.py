# License: LGPL
#
# Copyright: Brainwy Software

import collections
from pyvmmonitor_core import compat


class OrderedSet(collections.MutableSet):

    def __init__(self, initial=()):
        self._dict = collections.OrderedDict()
        for a in initial:
            self.add(a)

    def update(self, *args):
        for s in args:
            for e in s:
                self.add(e)

    def index(self, elem):
        for i, key in enumerate(compat.iterkeys(self._dict)):
            if key == elem:
                return i
        return -1

    def __contains__(self, x):
        return x in self._dict

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def item_at(self, i):
        return compat.keys(self._dict)[i]

    def add(self, elem):
        self._dict[elem] = None

    def discard(self, elem):
        self._dict.pop(elem, None)

    def __repr__(self):
        return 'OrderedSet([%s])' % (', '.join(map(repr, compat.iterkeys(self._dict))))

    def __str__(self):
        return '{%s}' % (', '.join(map(repr, compat.iterkeys(self._dict))))

    def popitem(self, last=True):
        return self._dict.popitem(last=last)
