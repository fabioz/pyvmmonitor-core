import pytest

from pyvmmonitor_core.ordered_set import OrderedSet
from pyvmmonitor_core.weak_utils import WeakList


class Stub(object):

    created = WeakList()

    def __init__(self, data):
        self.data = data
        self.created.append(self)

    def __hash__(self, *args, **kwargs):
        return self.data

    def __eq__(self, o):
        if isinstance(o, Stub):
            return self.data == o.data

        return False

    def __ne__(self, o):
        return not self == o

    def __repr__(self):
        return str(self.data)

    __str__ = __repr__


def test_ordered_set():

    s = OrderedSet([Stub(1), Stub(2)])

    s.add(Stub(3))
    assert list(s) == [Stub(1), Stub(2), Stub(3)]
    s.discard(Stub(2))
    assert list(s) == [Stub(1), Stub(3)]
    assert list(reversed(s)) == [Stub(3), Stub(1)]
    assert s.index(Stub(3)) == 1
    repr(s)
    str(s)
    assert s.item_at(1) == Stub(3)

    assert len(s) == 2

    assert s == OrderedSet([Stub(1), Stub(3)])
    s.clear()
    assert len(Stub.created) == 0, 'Stub objects not garbage-collected!'

    s = OrderedSet([Stub(1), Stub(3)])
    s.add(Stub(1))
    assert list(s) == [Stub(1), Stub(3)]

    s.add(Stub(4))
    assert list(s) == [Stub(1), Stub(3), Stub(4)]

    with pytest.raises(KeyError):
        OrderedSet().popitem(last=False)
    with pytest.raises(KeyError):
        OrderedSet().popitem(last=True)

    s.popitem(last=False)
    assert list(s) == [Stub(3), Stub(4)]
    s.popitem(last=True)
    assert list(s) == [Stub(3)]

    s.insert_before(Stub(3), Stub(4))
    assert list(s) == [Stub(4), Stub(3)]
    assert Stub(4) in s

    s.insert_before(Stub(4), Stub(5))
    assert list(s) == [Stub(5), Stub(4), Stub(3)]

    s.insert_before(Stub(3), Stub(9))
    assert list(s) == [Stub(5), Stub(4), Stub(9), Stub(3)]

    s.insert_before(Stub(5), Stub(8))
    expected = [Stub(8), Stub(5), Stub(4), Stub(9), Stub(3)]
    assert list(s) == expected
    for e in expected:
        assert e in s

    assert list(reversed(s)) == list(reversed(expected))
    s.discard(Stub(8))
    assert list(s) == [Stub(5), Stub(4), Stub(9), Stub(3)]

    del e
    del expected

    s.move_to_end(Stub(4))
    assert list(s) == [Stub(5), Stub(9), Stub(3), Stub(4)]

    s.move_to_beginning(Stub(4))
    assert list(s) == [Stub(4), Stub(5), Stub(9), Stub(3)]

    s.move_to_previous(Stub(5))
    assert list(s) == [Stub(5), Stub(4), Stub(9), Stub(3)]

    s.move_to_previous(Stub(5))
    assert list(s) == [Stub(5), Stub(4), Stub(9), Stub(3)]

    s.move_to_next(Stub(5))
    assert list(s) == [Stub(4), Stub(5), Stub(9), Stub(3)]

    s.move_to_next(Stub(3))
    assert list(s) == [Stub(4), Stub(5), Stub(9), Stub(3)]

    assert s.get_previous(Stub(4)) is None
    assert s.get_previous(Stub(3)) == Stub(9)

    assert s.get_next(Stub(4)) == Stub(5)
    assert s.get_next(Stub(3)) is None

    s.clear()
    assert len(Stub.created) == 0, 'Stub objects not garbage-collected!'


def test_ordered_set2():

    s = OrderedSet()
    s.add(Stub(1))
    assert list(s) == [Stub(1)]

    s.add(Stub(2))
    assert list(s) == [Stub(1), Stub(2)]

    s.add(Stub(3))
    assert list(s) == [Stub(1), Stub(2), Stub(3)]
    assert list(reversed(s)) == [Stub(3), Stub(2), Stub(1)]

    s.discard(Stub(1))
    assert list(s) == [Stub(2), Stub(3)]

    s.discard(Stub(3))
    assert list(s) == [Stub(2)]

    s.discard(Stub(2))
    assert list(s) == []

    assert len(Stub.created) == 0, 'Stub objects not garbage-collected!'
