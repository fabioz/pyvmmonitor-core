

class _Dummy(object):
    pass


def test_weaklist():
    from pyvmmonitor_core.weak_utils import WeakList
    l = WeakList()
    d1 = _Dummy()
    l.append(d1)
    assert len(list(l)) == 1
    l.clear()
    assert len(list(l)) == 0
    l.append(d1)
    assert len(list(l)) == 1
    d1 = None
    assert len(list(l)) == 0

    d1 = _Dummy()
    d2 = _Dummy()
    l.append(d1)
    l.append(d2)
    assert len(list(l)) == 2
    l.remove(d1)
    assert len(list(l)) == 1
    l.remove(d1)
    assert len(list(l)) == 1
    assert len(l) == 1


def test_weak_ordered_set():
    from pyvmmonitor_core.weak_utils import WeakOrderedSet
    s = WeakOrderedSet()
    d1 = _Dummy()
    s.add(d1)
    assert len(list(s)) == 1
    s.clear()
    assert len(list(s)) == 0
    s.add(d1)
    assert len(list(s)) == 1
    d1 = None
    assert len(list(s)) == 0

    d1 = _Dummy()
    d2 = _Dummy()
    s.add(d1)
    s.add(d2)
    assert len(list(s)) == 2
    s.remove(d1)
    assert len(list(s)) == 1
    s.discard(d1)
    assert len(list(s)) == 1
    assert len(s) == 1
