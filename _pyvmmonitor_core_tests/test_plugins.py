import pytest

from pyvmmonitor_core.plugins import PluginManager, NotRegisteredError,\
    InstanceAlreadyRegisteredError


class EPFoo(object):

    def __init__(self):
        self.foo = False

    def Foo(self):
        pass


class EPBar(object):

    def __init__(self):
        pass

    def Bar(self):
        pass


class FooImpl(EPFoo):

    def Foo(self):
        self.foo = True


class AnotherFooImpl(EPFoo):
    pass


def test_plugins():

    pm = PluginManager()
    pm.register(EPFoo, '_pyvmmonitor_core_tests.test_plugins.FooImpl', keep_instance=True)
    with pytest.raises(InstanceAlreadyRegisteredError):
        pm.register(
            EPFoo,
            '_pyvmmonitor_core_tests.test_plugins.AnotherFooImpl',
            keep_instance=True)

    foo = pm.get_instance(EPFoo)
    assert pm.get_instance(EPFoo) is foo
    # It's only registered in a way where the instance is kept
    assert not pm.get_implementations(EPFoo)

    assert not pm.get_implementations(EPBar)
    with pytest.raises(NotRegisteredError):
        pm.get_instance(EPBar)

    pm.register(
        EPFoo,
        '_pyvmmonitor_core_tests.test_plugins.AnotherFooImpl',
        context='context2',
        keep_instance=True)

    assert isinstance(pm.get_instance(EPFoo, context='context2'), AnotherFooImpl)
