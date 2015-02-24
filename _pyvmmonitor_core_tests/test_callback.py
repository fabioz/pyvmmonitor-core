from pyvmmonitor_core.callback import Callback
from pyvmmonitor_core.weak_utils import get_weakref


def test_callback():
    c = Callback()

    class F(object):
        def __init__(self):
            self.called = None

        def __call__(self, b):
            self.called = b

    f = F()
    c.register(f.__call__)
    assert len(c) == 1

    c(1)
    assert f.called == 1
    f = get_weakref(f)
    assert f() is None
    c(1)
    assert len(c) == 0


def test_callback2():
    c = Callback()

    class F(object):
        def __init__(self):
            self.called = None

        def __call__(self, b):
            self.called = b

    f = F()
    c.register(f)
    assert len(c) == 1

    c(1)
    assert f.called == 1
    f = get_weakref(f)
    assert f() is None
    c(1)
    assert len(c) == 0


def test_callback3():
    c = Callback()

    called = []

    # When we pass a function we'll create a strong reference!
    def strong_ref_to_method(b):
        called.append(b)

    c.register(strong_ref_to_method)
    assert len(c) == 1

    c(1)
    del strong_ref_to_method
    c(1)
    assert len(c) == 1
