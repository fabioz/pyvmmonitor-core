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

    def __reversed__(self):
        return reversed(self._dict)

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

    def insert_before(self, key, elem):
        assert elem not in self

        self._dict._OrderedDict__map[elem] = new_link = collections._Link()
        new_link.key = elem

        odict_map = self._dict._OrderedDict__map
        odict_map[elem] = new_link
        dict.__setitem__(self._dict, elem, None)
        add_before_link = odict_map[key]

        new_link.prev = add_before_link.prev
        new_link.next = add_before_link
        add_before_link.prev = new_link
        new_link.prev.next = new_link

        root = self._dict._OrderedDict__root

        if root.next is add_before_link:
            root.next = new_link
