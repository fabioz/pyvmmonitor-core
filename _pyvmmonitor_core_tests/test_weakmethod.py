def test_weakmethod():
    from pyvmmonitor_core.weakmethod import WeakMethodProxy

    class Object(object):
        def foo(self):
            return 1

    obj = Object()
    proxy = WeakMethodProxy(obj.foo)
    assert proxy() == 1
    del obj
    assert proxy() is None
