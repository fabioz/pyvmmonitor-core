'''
A feature-rich ordered set (which allows reordering internal items).

License: MIT

Copyright: Brainwy Software
'''

try:
    from collections.abc import MutableSet
except ImportError:
    from collections import MutableSet
from weakref import ref


class _Node(object):
    __slots__ = ['prev', 'next', 'el', '__weakref__']


class OrderedSet(MutableSet):
    '''
    Some notes:

    self._end.next is actually the first element of the internal double linked list
    self._end.prev is the last element

    Almost all operations should be fast O(1), except "index, item_at", which are O(n):
    '''

    def __init__(self, initial=()):
        end = self._end = _Node()

        root_ref = self._root_ref = ref(end)
        end.prev = root_ref
        end.next = root_ref
        self._dict = {}

        for a in initial:
            self.add(a)

    def add(self, el):
        if el not in self._dict:
            node = _Node()
            node.el = el

            root = self._end
            curr_ref = root.prev
            curr = curr_ref()
            node.prev = curr_ref
            node.next = self._root_ref
            self._dict[el] = node
            curr.next = root.prev = ref(node)

    def update(self, *args):
        for s in args:
            for e in s:
                self.add(e)

    def index(self, elem):
        # Note: this is a slow operation!
        for i, el in enumerate(self):
            if el == elem:
                return i
        return -1

    def __contains__(self, x):
        return x in self._dict

    def __iter__(self):
        root = self._end
        node = root.next()

        while node is not root:
            yield node.el
            node = node.next()

    def __reversed__(self):
        root = self._end
        curr = root.prev()
        while curr is not root:
            yield curr.el
            curr = curr.prev()

    def discard(self, el):
        entry = self._dict.pop(el, None)
        if entry is not None:
            # Set a ref with a ref is ok.
            entry.prev().next = entry.next
            entry.next().prev = entry.prev

    def item_at(self, i):
        if i < 0:
            it = reversed(self)
            i = abs(i) - 1
        else:
            it = self

        # Note: this is a slow operation (unless it's something as i = 0 or i = -1)
        for k, el in enumerate(it):
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
        ret = self.pop(last)
        # Kept for backward compatibility (was returning popitem from odict mapping key=key).
        # Should probably be deprecated going forward.
        return ret, ret

    def pop(self, last=True):
        if last:
            node = self._end.prev()
        else:
            node = self._end.next()

        if node is self._end:
            raise KeyError('empty')
        ret = node.el
        self.discard(ret)
        return ret

    def insert_before(self, el_before, el):
        '''
        Insert el before el_before
        '''
        assert el not in self._dict
        assert el_before in self._dict

        new_link = _Node()
        new_link.el = el
        self._dict[el] = new_link

        add_before_link = self._dict[el_before]

        new_link.prev = add_before_link.prev
        new_link.next = ref(add_before_link)
        new_link_ref = ref(new_link)
        add_before_link.prev = new_link_ref
        new_link.prev().next = new_link_ref

    def insert_after(self, el_after, el):
        '''
        Insert el after el_after
        '''
        assert el not in self._dict
        assert el_after in self._dict

        new_link = _Node()
        new_link.el = el
        self._dict[el] = new_link

        add_after_link = self._dict[el_after]

        new_link.next = add_after_link.next
        new_link.prev = ref(add_after_link)
        new_link_ref = ref(new_link)
        add_after_link.next = new_link_ref
        new_link.next().prev = new_link_ref

    def move_to_beginning(self, el):
        self.discard(el)
        if not self._dict:
            self.add(el)
        else:
            root = self._end
            node = root.next()
            self.insert_before(node.el, el)

    def move_to_end(self, el):
        self.discard(el)
        self.add(el)

    def move_to_previous(self, el):
        node = self._dict[el]
        if len(self._dict) > 1 and self._end.next().el != el:
            before_key = node.prev().el
            self.discard(el)
            self.insert_before(before_key, el)

    def move_to_next(self, el):
        node = self._dict[el]
        if len(self._dict) > 1 and self._end.prev().el != el:
            after_key = node.next().el
            self.discard(el)
            self.insert_after(after_key, el)

    def get_previous(self, el):
        node = self._dict[el]
        prev = node.prev()
        if prev is self._end:
            return None
        return prev.el

    def get_next(self, el):
        node = self._dict[el]
        next_node = node.next()
        if next_node is self._end:
            return None
        return next_node.el
