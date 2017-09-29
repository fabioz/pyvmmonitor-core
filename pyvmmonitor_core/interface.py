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

Note: results are cached for faster access afterwards and the cache-key is the tuple(cls,
interface), so, classes won't be garbage-collected after a check (usually classes don't die and this
isn't a problem, but it may be the source of leaks in applications which create classes and expect
them to die when no longer referenced).

License: LGPL

Copyright: Brainwy Software
'''

import inspect
import sys
from collections import namedtuple

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
    for method_name in _get_methods(interface_class):
        if method_name not in cls_methods:
            found = False
        else:
            method_in_cls = getattr(cls, method_name)
            method_in_interface = getattr(interface_class, method_name)
            if method_in_cls == method_in_interface:
                found = False  # Interface subclass but doesn't override method_name.
            else:
                found = True

        if not found:
            impl_details = _cache[key] = ImplDetails(
                False, '%s.%s not available.\n\nExpected: %s\nto implement: %s\nFrom: %s' %
                (cls.__name__, method_name, cls, method_name, interface_class))

            return impl_details
        else:
            # Let's see if parameters match
            cls_args, cls_varargs, cls_varkw, cls_defaults = inspect.getargspec(method_in_cls)

            if cls_varargs is not None and cls_varkw is not None:
                if not cls_args or cls_args == ['self'] or cls_args == ['cls']:
                    # (*args, **kwargs), (self, *args, **kwargs) and (cls, *args, **kwargs)
                    # always match
                    continue

            interf_args, interf_varargs, interf_varkw, interf_defaults = inspect.getargspec(
                method_in_interface)

            # Now, let's see if parameters actually match the interface parameters.
            if interf_varargs is not None and cls_varargs is None or \
                    interf_varkw is not None and cls_varkw is None or \
                    interf_args != cls_args or \
                    interf_defaults != cls_defaults:
                interface_signature = inspect.formatargspec(
                    interf_args, interf_varargs, interf_varkw, interf_defaults)

                class_signature = inspect.formatargspec(
                    cls_args, cls_varargs, cls_varkw, cls_defaults)

                msg = ("\nMethod params in %s.%s:\n"
                       "  %s\ndon't match params in %s.%s\n  %s")
                msg = msg % (cls.__name__, method_name, class_signature,
                             interface_class.__name__, method_name, interface_signature)

                impl_details = _cache[key] = ImplDetails(False, msg)

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
            details = _impl_details(cls, interface_class)
            if details.msg:
                raise BadImplementationError(details.msg)
        return cls
    return func
