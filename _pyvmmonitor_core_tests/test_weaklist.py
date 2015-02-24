from pyvmmonitor_core.weak_utils import WeakList


class _Dummy(object):
    pass


def test_weaklist():
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
