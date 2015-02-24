'''
Copyright: ESSS - Engineering Simulation and Scientific Software Ltda
License: LGPL

From: https://github.com/ESSS/ben10/blob/master/source/python/ben10/foundation/weak_ref.py

Weak reference to bound-methods. This allows the client to hold a bound method
while allowing GC to work.

Based on recipe from Python Cookbook, page 191. Differs by only working on
boundmethods and returning a true boundmethod in the __call__() function.
'''
try:
    import new
except ImportError:
    import types as new
import weakref

try:
    ReferenceError = weakref.ReferenceError
except AttributeError:
    ReferenceError = ReferenceError


class WeakMethod(object):
    '''
    Keeps a reference to an object but doesn't prevent that object from being garbage collected
    (unless it's a function)
    '''

    __slots__ = [
        '_obj',
        '_func',
        '_class',
        '_hash',
        '__weakref__'  # We need this to be able to add weak references.
    ]

    def __init__(self, method):
        try:
            if method.im_self is not None:
                # bound method
                self._obj = weakref.ref(method.im_self)
            else:
                # unbound method
                self._obj = None
            self._func = method.im_func
            self._class = method.im_class
        except AttributeError:
            # For functions leave strong references.
            self._obj = None
            self._func = method
            self._class = None

    def __call__(self):
        '''
        Return a new bound-method like the original, or the original function if refers just to
        a function or unbound method.

        @return:
            None if the original object doesn't exist anymore.
        '''
        if self.is_dead():
            return None
        if self._obj is not None:
            # we have an instance: return a bound method
            return new.instancemethod(self._func, self._obj(), self._class)
        else:
            # we don't have an instance: return just the function
            return self._func

    def is_dead(self):
        '''
        Returns True if the referenced callable was a bound method and
        the instance no longer exists. Otherwise, return False.
        '''
        return self._obj is not None and self._obj() is None

    def __eq__(self, other):
        try:
            return isinstance(self, type(other)) and self() == other()
        except:
            return False

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        if not hasattr(self, '_hash'):
            # The hash should be immutable (must be calculated once and never changed -- otherwise
            # we won't be able to get it when the object dies)
            self._hash = hash(WeakMethod.__call__(self))

        return self._hash

    def __repr__(self):
        func_name = getattr(self._func, '__name__', str(self._func))
        if self._obj is not None:
            obj = self._obj()
            if obj is None:
                obj_str = '<dead>'
            else:
                obj_str = '%X' % id(obj)
            msg = '<WeakMethod to %s.%s for object %s>'
            return msg % (self._class.__name__, func_name, obj_str)
        else:
            return '<WeakMethod to %s>' % func_name


class WeakMethodProxy(WeakMethod):
    '''
    Like ref, but calling it will cause the referent method to be called with the same
    arguments. If the referent's object no longer lives, ReferenceError is raised.
    '''

    def __call__(self, *args, **kwargs):
        func = WeakMethod.__call__(self)
        if func is None:
            raise ReferenceError('Object is dead. Was of class: %s' % (self._class,))
        else:
            return func(*args, **kwargs)

    def __eq__(self, other):
        try:
            func1 = WeakMethod.__call__(self)
            func2 = WeakMethod.__call__(other)
            return isinstance(self, type(other)) and func1 == func2
        except:
            return False
