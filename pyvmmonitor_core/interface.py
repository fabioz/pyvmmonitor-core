'''
Module with basic functionality for declaring/verifying interfaces on Python.

It's recommended that interfaces start with 'I' (although it's not enforced).

Any object can be used as an interface (which implies all the methods in the class
are virtual and should be implemented by an implementor of such interface).

Example:

    class ISomething(object):
        def do_something(self):
            """
            Do something here
            """

    @interface.check_implements(ISomething)
    class SomethingImpl(object):

        # @implements is optional, for documentation purposes (will inherit docstring).
        @implements(ISomething.do_something)
        def do_something(self):
            pass

Alternatively, it's possible to check if some object implements a given interface with:

    interface.is_implementation(obj, ISomething)

or assert it:

    interface.assert_implements(obj, ISomething)
'''

from collections import namedtuple
import inspect
import sys

from pyvmmonitor_core.memoization import memoize


class BadImplementationError(Exception):
    pass


_obj_methods = frozenset(dir(object))
_PY2 = sys.version_info[0] == 2


@memoize
def _get_methods(interface_class):
    obj_methods = _obj_methods
    ret = []
    for method_name in dir(interface_class):
        if method_name not in obj_methods:
            m = getattr(interface_class, method_name)
            if inspect.isfunction(m) or inspect.ismethod(m):
                ret.append(method_name)
    return frozenset(ret)


ImplDetails = namedtuple('ImplDetails', 'is_impl msg'.split())
_cache = {}


if _PY2:
    from new import classobj  # @UnresolvedImport

    def _is_class(obj):
        return isinstance(obj, (type, classobj))
else:
    def _is_class(obj):
        return isinstance(obj, type)


def _impl_details(cls_or_obj, interface_class):
    if _is_class(cls_or_obj):
        cls = cls_or_obj
    else:
        cls = cls_or_obj.__class__

    key = (cls, interface_class)
    ret = _cache.get(key)
    if ret is not None:
        return ret

    cls_methods = _get_methods(cls)
    for method in _get_methods(interface_class):
        if method not in cls_methods:
            found = False
        else:
            method_in_cls = getattr(cls, method)
            method_in_interface = getattr(interface_class, method)
            if method_in_cls == method_in_interface:
                found = False  # Interface subclass but doesn't override method.
            else:
                found = True

        if not found:
            impl_details = _cache[key] = ImplDetails(
                False, '%s.%s not available.\n\nExpected: %s\nto implement: %s\nFrom: %s' %
                (cls.__name__, method, cls, method, cls))

            return impl_details

    impl_details = _cache[key] = ImplDetails(True, None)
    return impl_details


def assert_implements(cls_or_obj, interface_class):
    '''
    :raise BadImplementationError:
        If the given object doesn't implement the passed interface.
    '''
    details = _impl_details(cls_or_obj, interface_class)
    if details.msg:
        raise BadImplementationError(details.msg)


def is_implementation(cls_or_obj, interface_class):
    '''
    :return bool:
        True if the given object implements the passed interface (and False otherwise).
    '''
    details = _impl_details(cls_or_obj, interface_class)
    return details.is_impl


def check_implements(*interface_classes):
    '''
    To be used as decorator:

    class ISomething(object):
        def m1(self):
            pass

    @interface.check_implements(ISomething)
    class SomethingImpl(object):
        pass

    '''
    def func(cls):
        for interface_class in interface_classes:
            assert_implements(cls, interface_class)
        return cls
    return func
