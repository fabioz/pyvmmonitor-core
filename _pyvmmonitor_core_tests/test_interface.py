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
