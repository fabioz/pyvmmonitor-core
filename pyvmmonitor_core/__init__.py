# License: LGPL
#
# Copyright: Brainwy Software
import os
import sys
from functools import wraps

__file__ = os.path.abspath(__file__)


def get_public_api_location():
    basedir = os.path.dirname(os.path.dirname(__file__))
    public_api = os.path.join(basedir, 'public_api')
    if os.path.exists(public_api):
        # In dev mode we don't really use the public_api dir, we use
        # the module dir directly.
        return public_api
    return basedir


def overrides(method_overridden):
    '''
    This is just an 'annotation' method to say that some method is overridden.

    It also checks that the method name is the same.
    '''

    def wrapper(func):
        if func.__name__ != method_overridden.__name__:
            msg = "Wrong @overrides: %r expected, but overwriting %r."
            msg = msg % (func.__name__, method_overridden.__name__)
            raise AssertionError(msg)

        if func.__doc__ is None:
            # inherit docs if it's not there already.
            func.__doc__ = method_overridden.__doc__

        return func

    return wrapper


def implements(method_implemented):
    '''
    This is just an 'annotation' method to say that some method is implemented.

    It also checks that the method name is the same.
    '''

    def wrapper(func):
        if hasattr(method_implemented, '__name__'):
            if func.__name__ != method_implemented.__name__:
                msg = "Wrong @implements: %r expected, but implementing %r."
                msg = msg % (func.__name__, method_implemented.__name__)
                raise AssertionError(msg)

        if func.__doc__ is None:
            # inherit docs if it's not there already.
            func.__doc__ = method_implemented.__doc__

        return func

    return wrapper


def is_frozen():
    return getattr(sys, 'frozen', False)


_is_development = not is_frozen()


def is_development():
    '''
    Note: although it's initialized to be the opposite of the frozen, it has a different semantic.

    I.e.: frozen means we're executing from a zip with a different layout and is_development on the
    other way should be used to do additional checks and asserts (and we could set the development
    mode to True even when frozen).
    '''
    return _is_development


def abstract(func):
    '''
    Marks some method as abstract (meaning it has to be overridden in a subclass).
    '''

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        msg = 'Method %r must be implemented in class %r.' % (func.__name__, self.__class__)
        raise NotImplementedError(msg)

    return wrapper


if __name__ == '__main__':

    class A(object):

        def m1(self):
            pass

    class B(A):

        @overrides(A.m1)
        def m1(self):
            pass

        @abstract
        def m2(self):
            pass

    assert B.m1.__name__ == 'm1'
