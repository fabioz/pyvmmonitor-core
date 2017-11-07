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
def _get_methods_and_properties(interface_class):
    obj_methods = _obj_methods
    ret = []
    for method_name in dir(interface_class):
        if method_name not in obj_methods:
            m = getattr(interface_class, method_name)
            if inspect.isfunction(m) or inspect.ismethod(m) or m.__class__ == property:
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

    cls_methods_and_properties = _get_methods_and_properties(cls)
    for method_or_prop_name in _get_methods_and_properties(interface_class):
        if method_or_prop_name not in cls_methods_and_properties:
            found = False
        else:
            method_in_cls = getattr(cls, method_or_prop_name)
            method_in_interface = getattr(interface_class, method_or_prop_name)
            if method_in_cls == method_in_interface:
                found = False  # Interface subclass but doesn't override method_or_prop_name.
            else:
                found = True

        if not found:
            impl_details = _cache[key] = ImplDetails(
                False, '%s.%s not available.\n\nExpected: %s\nto implement: %s\nFrom: %s' %
                (cls.__name__, method_or_prop_name, cls, method_or_prop_name, interface_class))

            return impl_details
        else:
            if method_in_interface.__class__ == property:
                if method_in_cls.__class__ != property:
                    msg = ('Expected %s to be a property in %s' % (
                        cls.__name__, method_or_prop_name))
                    impl_details = _cache[key] = ImplDetails(False, msg)
                    return impl_details

                if method_in_interface.fdel is not None:
                    if method_in_cls.fdel is None:
                        msg = ('Expected fdel in %s.%s property.' % (
                            cls.__name__, method_or_prop_name))
                        impl_details = _cache[key] = ImplDetails(False, msg)
                        return impl_details

                if method_in_interface.fset is not None:
                    if method_in_cls.fset is None:
                        msg = ('Expected fset in %s.%s property.' % (
                            cls.__name__, method_or_prop_name))
                        impl_details = _cache[key] = ImplDetails(False, msg)
                        return impl_details

                # No need to check fget (should always be there).
                continue

            # Let's see if parameters match
            try:
                cls_args, cls_varargs, cls_varkw, cls_defaults = inspect.getargspec(method_in_cls)
                cls_kwonlyargs = None
                cls_kwonlydefaults = None
            except ValueError:
                cls_args, cls_varargs, cls_varkw, cls_defaults, cls_kwonlyargs, \
                    cls_kwonlydefaults, _ = inspect.getfullargspec(method_in_cls)

            if cls_varargs is not None and cls_varkw is not None:
                if not cls_args or cls_args == ['self'] or cls_args == ['cls']:
                    # (*args, **kwargs), (self, *args, **kwargs) and (cls, *args, **kwargs)
                    # always match
                    continue

            try:
                interf_args, interf_varargs, interf_varkw, interf_defaults = inspect.getargspec(
                    method_in_interface)
                interf_kwonlyargs = None
                interf_kwonlydefaults = None
            except ValueError:
                interf_args, interf_varargs, interf_varkw, interf_defaults, interf_kwonlyargs, \
                    interf_kwonlydefaults, _interf_annotations = inspect.getfullargspec(
                        method_in_interface)

            # Now, let's see if parameters actually match the interface parameters.
            if interf_varargs is not None and cls_varargs is None or \
                    interf_varkw is not None and cls_varkw is None or \
                    interf_args != cls_args or \
                    interf_defaults != cls_defaults or \
                    interf_kwonlyargs != cls_kwonlyargs or \
                    interf_kwonlydefaults != cls_kwonlydefaults:

                if _PY2:
                    interface_signature = inspect.formatargspec(
                        interf_args, interf_varargs, interf_varkw, interf_defaults)

                    class_signature = inspect.formatargspec(
                        cls_args, cls_varargs, cls_varkw, cls_defaults)
                else:
                    interface_signature = inspect.formatargspec(
                        interf_args, interf_varargs, interf_varkw, interf_defaults,
                        interf_kwonlyargs, interf_kwonlydefaults)

                    class_signature = inspect.formatargspec(
                        cls_args, cls_varargs, cls_varkw, cls_defaults, cls_kwonlyargs,
                        cls_kwonlydefaults)

                msg = ("\nMethod params in %s.%s:\n"
                       "  %s\ndon't match params in %s.%s\n  %s")
                msg = msg % (cls.__name__, method_or_prop_name, class_signature,
                             interface_class.__name__, method_or_prop_name, interface_signature)

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
