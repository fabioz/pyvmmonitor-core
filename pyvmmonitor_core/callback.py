'''
Copyright: ESSS - Engineering Simulation and Scientific Software Ltda
License: LGPL

Based on: https://github.com/ESSS/ben10/blob/master/source/python/ben10/foundation/callback.py
'''
from collections import OrderedDict as odict
import sys
import types
import weakref

from pyvmmonitor_core.thread_utils import is_in_main_thread
try:
    import new
except ImportError:
    import types as new


class Callback(object):
    '''
    Object that provides a way for others to connect in it and later call it to call
    those connected.

    .. note:: This implementation is improved in that it works directly accessing functions based
    on a key in an ordered dict, so, register, unregister and contains are much faster than the
    old callback.

    .. note:: it only stores weakrefs to objects connected

    .. note:: __slots__ added, so, it cannot have weakrefs to it (but as it stores weakrefs
        internally, that shouldn't be a problem). If weakrefs are really needed,
        __weakref__ should be added to the slots.
    '''
    __call_out_of_main_thread__ = True

    __slots__ = [
        '_callbacks',
        '__weakref__'  # We need this to be able to add weak references to callback objects.
    ]

    def __init__(self):
        self._callbacks = odict()

    def _get_key(self, func):
        '''
        :param object func:
            The function for which we want the key.

        :rtype: object
        :returns:
            Returns the key to be used to access the object.

        .. note:: The key is guaranteed to be unique among the living objects, but if the object
        is garbage collected, a new function may end up having the same key.
        '''
        try:
            if func.im_self is not None:
                # bound method
                return (id(func.im_self), id(func.im_func), id(func.im_class))
            else:
                return (id(func.im_func), id(func.im_class))

        except AttributeError:
            return id(func)

    def _get_info(self, func):
        '''
        :rtype: tuple(func_obj, func_func, func_class)
        :returns:
            Returns a tuple with the information needed to call a method later on (close to the
            WeakMethodRef, but a bit more specialized -- and faster for this context).
        '''
        # Note: if it's a _CallbackWrapper, we want to register it and not the 'original method'
        # at this point
        try:
            if func.im_self is not None:
                # bound method
                return (weakref.ref(func.im_self), func.im_func, func.im_class)
            else:
                # unbound method
                return (None, func.im_func, func.im_class)
        except AttributeError:
            if not isinstance(func, types.FunctionType):
                # Deal with an instance
                return (weakref.ref(func), None, None)
            else:
                # Not a method -- a callable: create a strong reference
                # Why you may ask? Well, the main reason is that this use-case is usually for
                # closures, so, it may be hard to find a place to add the instance -- and if
                # it's a top level, the function will be alive until the end of times anyway.
                #
                # Anyways, this is probably a case that should only be used with care as
                # unregistering must be explicit and things in the function scope will be
                # kept alive!
                return (None, func, None)

    def __call__(self, *args, **kwargs):
        '''
        Calls every registered function with the given args and kwargs.
        '''
        callbacks = self._callbacks
        if not callbacks:
            return

        # Note: There's a copy of this code in the _calculate_to_call method below. It's a copy
        # because we don't want to had a function call overhead here.
        to_call = []

        for key, info in callbacks.items():  # iterate in a copy

            func_obj = info[0]
            if func_obj is not None:
                # Ok, we have a self.
                func_obj = func_obj()
                if func_obj is None:
                    # self is dead
                    del callbacks[key]
                else:
                    func_func = info[1]
                    if func_func is None:
                        to_call.append(func_obj)
                    else:
                        to_call.append(new.instancemethod(func_func, func_obj, info[2]))
            else:
                func_func = info[1]

                # No self: either classmethod or just callable
                to_call.append(func_func)

        # let's keep the 'if' outside of the iteration...
        if not is_in_main_thread():
            for func in to_call:
                if not getattr(func, '__call_out_of_main_thread__', False):
                    raise AssertionError(
                        'Call: %s out of the main thread (and it is not marked as @not_main_thread_callback)!' %
                        (func,))

        for func in to_call:
            try:
                func(*args, **kwargs)
            except:
                # Show it but don't propagate.
                sys.excepthook(*sys.exc_info())

    def register(self, func):
        '''
        Registers a function in the callback.

        :param object func:
            Method or function that will be called later.
        '''
        key = self._get_key(func)
        callbacks = self._callbacks

        callbacks.pop(key, None)  # remove if it exists
        callbacks[key] = self._get_info(func)

    def unregister(self, func):
        '''
        unregister a function previously registered with register.

        :param object func:
            The function to be unregistered.
        '''
        key = self._get_key(func)

        try:
            # As there can only be 1 instance with the same id alive, it should be OK just
            # deleting it directly (because if there was a dead reference pointing to it it will
            # be already dead anyways)
            del self._callbacks[key]
        except (KeyError, AttributeError):
            # Even when unregistering some function that isn't registered we shouldn't trigger an
            # exception, just do nothing
            pass

    def unregister_all(self):
        '''
        Unregisters all functions
        '''
        self._callbacks.clear()

    def __len__(self):
        return len(self._callbacks)


def not_main_thread_callback(func):
    func.__call_out_of_main_thread__ = True
    return func
