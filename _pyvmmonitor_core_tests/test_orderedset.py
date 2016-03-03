from pyvmmonitor_core.ordered_set import OrderedSet


def test_ordered_set():
    s = OrderedSet([1, 2])
    s.add(3)
    assert list(s) == [1, 2, 3]
    s.discard(2)
    assert list(s) == [1, 3]
    assert list(reversed(s)) == [3, 1]
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

    s.insert_before(3, 4)
    assert list(s) == [4, 3]
    assert 4 in s

    s.insert_before(4, 5)
    assert list(s) == [5, 4, 3]

    s.insert_before(3, 9)
    assert list(s) == [5, 4, 9, 3]

    s.insert_before(5, 8)
    expected = [8, 5, 4, 9, 3]
    assert list(s) == expected
    for e in expected:
        assert e in s

    assert list(reversed(s)) == list(reversed(expected))
    s.discard(8)
    assert list(s) == [5, 4, 9, 3]
