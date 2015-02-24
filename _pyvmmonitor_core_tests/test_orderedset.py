from pyvmmonitor_core.ordered_set import OrderedSet


def test_ordered_set():
    s = OrderedSet([1, 2])
    s.add(3)
    assert list(s) == [1, 2, 3]
    s.discard(2)
    assert list(s) == [1, 3]
    assert s.index(3) == 1
    repr(s)
    str(s)
    assert s.item_at(1) == 3

    assert len(s) == 2

    assert s == OrderedSet([1, 3])

    s.add(1)
    assert list(s) == [1, 3]

    s.add(4)
    assert list(s) == [1, 3, 4]

    s.popitem(last=False)
    assert list(s) == [3, 4]
    s.popitem(last=True)
    assert list(s) == [3]
