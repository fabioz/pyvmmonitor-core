import pytest


def test_interfaces():
    from pyvmmonitor_core import interface
    from pyvmmonitor_core.interface import BadImplementationError

    class ISomething(object):

        def m1(self):
            pass

    @interface.check_implements(ISomething)
    class SomethingImpl(object):

        def m1(self):
            pass

    s = SomethingImpl()
    assert interface.is_implementation(s, ISomething)
    assert interface.is_implementation(SomethingImpl, ISomething)

    with pytest.raises(BadImplementationError):

        @interface.check_implements(ISomething)
        class NoImpl(object):
            pass

    with pytest.raises(BadImplementationError):

        @interface.check_implements(ISomething)
        class NoImplDerivingFromInterface(ISomething):
            pass


def test_interfaces_match_params():
    from pyvmmonitor_core import interface
    from pyvmmonitor_core.interface import BadImplementationError

    class ISomething(object):

        def m1(self, a):
            pass

    @interface.check_implements(ISomething)
    class SomethingImpl(object):

        def m1(self, a):
            pass

    s = SomethingImpl()
    assert interface.is_implementation(s, ISomething)
    assert interface.is_implementation(SomethingImpl, ISomething)

    with pytest.raises(BadImplementationError):

        @interface.check_implements(ISomething)
        class NoImpl(object):

            def m1(self, bad_param):
                pass


def test_interfaces_full_argspec_required():
    import sys
    from _pyvmmonitor_core_tests import _py3_only
    if sys.version_info[0] <= 2:
        return

    from pyvmmonitor_core import interface
    from pyvmmonitor_core.interface import BadImplementationError
    ISomething = _py3_only.ISomething
    SomethingImplWrong = _py3_only.SomethingImplWrong
    SomethingImpl = _py3_only.SomethingImpl

    with pytest.raises(BadImplementationError):

        @interface.check_implements(ISomething)
        class SomethingImpl(object):

            def m1(self, a):
                pass

    with pytest.raises(BadImplementationError):
        interface.assert_implements(SomethingImplWrong, ISomething)

    interface.assert_implements(SomethingImpl, ISomething)


def test_interface_properties():

    from pyvmmonitor_core.interface import BadImplementationError

    class IFoo(object):

        @property
        def foo(self):
            pass

        @foo.setter
        def foo(self, foo):
            pass

    def check():
        from pyvmmonitor_core.interface import check_implements

        @check_implements(IFoo)
        class Foo(object):
            pass

    def check2():
        from pyvmmonitor_core.interface import check_implements

        @check_implements(IFoo)
        class Foo(object):

            @property
            def foo(self):
                pass

    def check3():
        from pyvmmonitor_core.interface import check_implements

        @check_implements(IFoo)
        class Foo(object):

            @property
            def foo(self):
                pass

            @foo.setter
            def foo(self, foo):
                pass

    with pytest.raises(BadImplementationError):
        check()

    with pytest.raises(BadImplementationError):
        check2()

    check3()
