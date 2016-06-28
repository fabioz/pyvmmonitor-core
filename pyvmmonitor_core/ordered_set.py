# License: MIT
#
# Copyright: Brainwy Software

import collections


class _Node(object):
    __slots__ = ['prev', 'next', 'el']


class OrderedSet(collections.MutableSet):
    '''
    Some notes:

    root.next is actually the first element of the internal double linked list
    root.prev is the last element
    '''

    def __init__(self, initial=()):
        root = self._end = _Node()

        root.prev = root
        root.next = root
        self._dict = {}

        for a in initial:
            self.add(a)

    def add(self, el):
        if el not in self._dict:
            node = _Node()
            node.el = el

            root = self._end
            curr = root.prev
            node.prev = curr
            node.next = root
            curr.next = root.prev = self._dict[el] = node

    def update(self, *args):
        for s in args:
            for e in s:
                self.add(e)

    def index(self, elem):
        for i, el in enumerate(self):
            if el == elem:
                return i
        return -1

    def __contains__(self, x):
        return x in self._dict

    def __iter__(self):
        root = self._end
        node = root.next

        while node is not root:
            yield node.el
            node = node.next

    def __reversed__(self):
        root = self._end
        curr = root.prev
        while curr is not root:
            yield curr.el
            curr = curr.prev

    def discard(self, el):
        entry = self._dict.pop(el, None)
        if entry is not None:
            entry.prev.next = entry.next
            entry.next.prev = entry.prev

    def item_at(self, i):
        for k, el in enumerate(self):
            if i == k:
                return el
        raise IndexError(i)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return 'OrderedSet([%s])' % (', '.join(map(repr, iter(self))))

    def __str__(self):
        return '{%s}' % (', '.join(map(repr, iter(self))))

    def popitem(self, last=True):
        if last:
            node = self._end.prev
        else:
            node = self._end.next

        if node is self._end:
            raise KeyError('empty')
        self.discard(node.el)

    def insert_before(self, key_before, el):
        '''
        Insert el before key_before
        '''
        assert el not in self._dict
        assert key_before in self._dict

        new_link = _Node()
        new_link.el = el
        self._dict[el] = new_link

        add_before_link = self._dict[key_before]

        new_link.prev = add_before_link.prev
        new_link.next = add_before_link
        add_before_link.prev = new_link
        new_link.prev.next = new_link

    def move_to_beginning(self, el):
        self.discard(el)
        if not self._dict:
            self.add(el)
        else:
            root = self._end
            node = root.next
            self.insert_before(node.el, el)

    def move_to_end(self, el):
        self.discard(el)
        self.add(el)

    def move_to_previous(self, el):
        node = self._dict[el]
        if len(self._dict) > 1 and self._end.next.el != el:
            before_key = node.prev.el
            self.discard(el)
            self.insert_before(before_key, el)
