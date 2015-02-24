# License: LGPL
#
# Copyright: Brainwy Software


def overrides(method):
    '''
    This is just an 'annotation' method to say that some method is overridden.

    It also checks that the method name is the same.
    '''
    def wrapper(func):
        if func.__name__ != method.__name__:
            msg = "Wrong @overrides: %r expected, but overwriting %r."
            msg = msg % (func.__name__, method.__name__)
            raise AssertionError(msg)

        if func.__doc__ is None:
            func.__doc__ = method.__doc__

        return func

    return wrapper


def implements(method):
    '''
    This is just an 'annotation' method to say that some method is implemented.

    It also checks that the method name is the same.
    '''
    def wrapper(func):
        if func.__name__ != method.__name__:
            msg = "Wrong @implements: %r expected, but implementing %r."
            msg = msg % (func.__name__, method.__name__)
            raise AssertionError(msg)

        if func.__doc__ is None:
            func.__doc__ = method.__doc__

        return func

    return wrapper

import sys


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

    def wrapper(self, *args, **kwargs):
        msg = 'Method %r must be implemented in class %r.' % (func.__name__, self.__class__)
        raise NotImplementedError(msg)

    wrapper.__name__ = func.__name__
    if func.__doc__ is not None:
        wrapper.__doc__ = func.__doc__
    return wrapper
