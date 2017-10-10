import sys
from contextlib import contextmanager

from pyvmmonitor_core import compat
from pyvmmonitor_core.callback import Callback

try:
    # Optional dependency: if greenlets are available check that properties aren't changed
    # when out of the main coroutine (the idea being that properties belong to main objects
    # in coroutines -- if this is a problem this can be relaxed later on).

    # It can also be locally disabled with:
    # from pyvmmonitor_core import props
    # with props.disable_in_coroutine_assert():
    #     ...
    import greenlet

    _disable_not_in_coroutine_assert = 0

    @contextmanager
    def disable_in_coroutine_assert():
        global _disable_not_in_coroutine_assert
        _disable_not_in_coroutine_assert += 1
        try:
            yield
        finally:
            _disable_not_in_coroutine_assert -= 1

    def _assert_not_in_coroutine():
        if _disable_not_in_coroutine_assert:
            return
        assert greenlet.getcurrent().parent is None, 'Did not expect to be in a coroutine'

except ImportError:
    # Add no-op version.
    def _assert_not_in_coroutine():
        pass

    @contextmanager
    def disable_in_coroutine_assert():
        yield


def _make_property(key, default):

    def get_val(self):
        return self._props.get(key, default)

    def set_val(self, val):
        # Note: coroutines are meant for pure functions, so, they shouldn't change anything.
        _assert_not_in_coroutine()
        prev = self._props.get(key, default)
        self._props[key] = val
        if prev != val:
            self._on_modified_callback(self, {key: (val, prev)})

    return property(get_val, set_val)


class PropsCustomProperty(object):

    def __init__(self, default):
        self.default = default

    def convert(self, obj, val):
        '''
        Subclasses may override to convert the value which is being set.
        '''
        return val

    def _make_property(outer_self, key):  # @NoSelf

        default = outer_self.default

        def get_val(self):
            return self._props.get(key, default)

        def set_val(self, val):
            # Note: coroutines are meant for pure functions, so, they shouldn't
            # change anything.
            _assert_not_in_coroutine()
            val = outer_self.convert(self, val)

            # Note: we're choosing to copy/paste the global "_make_property" to avoid
            # paying a function call.
            prev = self._props.get(key, default)
            self._props[key] = val
            if prev != val:
                self._on_modified_callback(self, {key: (val, prev)})

        return property(get_val, set_val)


class PropsObject(object):
    '''
    To use:

    class Point(PropsObject):

        PropsObject.declare_props(x=0, y=0)

        PropsObject.add_slot('_internal_attr')

    point = Point()

    def on_modified(obj, attrs):
        if 'x' in attrs:
            new_val, old_val = attrs['x']
            print('new x', new_val, 'old_x', old_val)

    point.register_modified(on_modified)
    '''

    __slots__ = ['_props', '_on_modified_callback', '__weakref__']

    @classmethod
    def declare_props(cls, **kwargs):
        frame = sys._getframe().f_back
        namespace = frame.f_locals

        props_namespace = namespace.get('__props__')
        if props_namespace is None:
            props_namespace = namespace['__props__'] = []

        for key, val in compat.iteritems(kwargs):
            if isinstance(val, PropsCustomProperty):
                namespace[key] = val._make_property(key)
            else:
                namespace[key] = _make_property(key, val)
            props_namespace.append(key)

        if '__slots__' not in namespace:
            namespace['__slots__'] = []

    @classmethod
    def add_slot(cls, slot):
        frame = sys._getframe().f_back
        namespace = frame.f_locals
        namespace['__slots__'].append(slot)

    def __init__(self, **kwargs):
        self._props = {}
        self._on_modified_callback = Callback()
        for key, val in compat.iteritems(kwargs):
            setattr(self, key, val)

    def register_modified(self, on_modified):
        self._on_modified_callback.register(on_modified)

    def unregister_modified(self, on_modified):
        self._on_modified_callback.unregister(on_modified)

    def create_memento(self):
        '''
        Note that the memento only includes the properties which were changed. To get all properties
        use get_props_as_dict.
        '''
        return dict((attr, getattr(self, attr)) for attr in self._props)

    def set_memento(self, memento):
        for key, val in compat.iteritems(memento):
            setattr(self, key, val)

    @classmethod
    def get_all_props_names(cls):
        all_props = getattr(cls, '__all_props__', None)
        if all_props is None:
            import inspect
            all_prop_names = set()
            all_prop_names.update(cls.__props__)
            for base_class in inspect.getmro(cls):
                # Can't recursively call get_all_props_names() as depending on the hierarchy it
                # wouldn't work.
                all_prop_names.update(getattr(base_class, '__props__', []))

            all_props = frozenset(all_prop_names)
            cls.__all_props__ = all_props
            cls.__all_props_cache_info__ = {'hit': 0}
        else:
            cls.__all_props_cache_info__['hit'] += 1

        return all_props

    def get_props_as_dict(self):
        ret = {}
        for prop in self.get_all_props_names():
            ret[prop] = getattr(self, prop)
        return ret

    @classmethod
    def delegate_to_props(cls, *props):
        frame = sys._getframe().f_back
        namespace = frame.f_locals

        for prop in props:
            namespace[prop] = _make_delegator_property(prop)


def _make_delegator_property(key):

    def get_val(self):
        return getattr(self._props, key)

    def set_val(self, val):
        return setattr(self._props, key, val)

    return property(get_val, set_val)
