# License: LGPL
#
# Copyright: Brainwy Software

'''
Defines a PluginManager (which doesn't really have plugins, only a registry of extension points
and implementations for such extension points).

To use, create the extension points you want (any class starting with 'EP') and register
implementations for those.

I.e.:

pm = PluginManager()
pm.register(EPFoo, '_pyvmmonitor_core_tests.test_plugins.FooImpl', keep_instance=True)
pm.register(EPBar, '_pyvmmonitor_core_tests.test_plugins.BarImpl', keep_instance=False)

Then, later, to use it it's possible to ask for instances through the PluginManager API:

foo_instances = pm.get_implementations(EPFoo) # Each time this is called, new
                                              # foo_instances will be created
bar_instance = pm.get_instance(EPBar) # Each time this is called, the same bar_instance is returned.

Alternatively, it's possible to use a decorator to use a dependency injection pattern -- i.e.:
don't call me, I'll call you ;)

@inject(foo_instance=EPFoo, bar_instances=[EPBar])
def m1(foo_instance, bar_instances, pm):
    for bar in bar_instances:
        ...

    foo_instance.foo

'''

import functools
import sys

from pyvmmonitor_core import compat
from pyvmmonitor_core.callback import Callback
from pyvmmonitor_core.lazy_loading import load_token
from pyvmmonitor_core.weak_utils import get_weakref

if sys.version_info[0] >= 3:
    string_types = (str,)
else:
    string_types = (unicode, str)

load_class = load_token  # Alias for backward compatibility


class NotInstanceError(RuntimeError):
    pass


class NotRegisteredError(RuntimeError):
    pass


class InstanceAlreadyRegisteredError(RuntimeError):
    pass


class IPluginsExit(object):

    def plugins_exit(self):
        pass


class PluginManager(object):

    '''
    This is a manager of plugins (which we refer to extension points and implementations).

    Mostly, we have a number of EPs (Extension Points) and implementations may be registered
    for those extension points.

    The PluginManager is able to provide implementations (through #get_implementations) which are
    not kept on being tracked and a special concept which keeps an instance alive for an extension
    (through #get_instance).

    Every instance registered will have:

    - a 'pm' attribute set to this PluginManager (which is a weak reference to the plugin manager).

    - a 'plugins_exit' method called if it defines it when the PluginManager is about to exit (if
      it defines one).
    '''

    def __init__(self):
        self._ep_to_impls = {}
        self._ep_to_instance_impls = {}
        self._ep_to_context_to_instance = {}
        self._name_to_ep = {}
        self.exited = False
        self.on_about_to_exit = Callback()

    def get_implementations(self, ep):
        assert not self.exited
        if ep.__class__ in string_types:
            ep = self._name_to_ep[ep]

        impls = self._ep_to_impls.get(ep, [])
        ret = []
        for impl, kwargs in impls:
            class_ = load_class(impl)
            instance = class_(**kwargs)
            instance.pm = get_weakref(self)
            ret.append(instance)

        return ret

    def register(self, ep, impl, kwargs={}, context=None, keep_instance=False):
        '''

        :param ep:
        :param str impl:
            This is the full path to the class implementation.

        :param kwargs:
        :param context:
            If keep_instance is True, it's possible to register it for a given
            context.

        :param keep_instance:
            If True, it'll be only available through pm.get_instance and the
            instance will be kept for further calls.
            If False, it'll only be available through get_implementations.
        '''
        assert not self.exited
        if ep.__class__ in string_types:
            raise ValueError('Expected the actual EP class to be passed.')
        self._name_to_ep[ep.__name__] = ep

        if keep_instance:
            register_at = self._ep_to_instance_impls
            impls = register_at.get((ep, context))
            if impls is None:
                impls = register_at[(ep, context)] = []
            else:
                raise InstanceAlreadyRegisteredError(
                    'Unable to override when instance is kept and an implementation '
                    'is already registered.')
        else:
            register_at = self._ep_to_impls
            impls = register_at.get(ep)
            if impls is None:
                impls = register_at[ep] = []

        impls.append((impl, kwargs))

    def set_instance(self, ep, instance, context=None):
        if ep.__class__ in string_types:
            raise ValueError('Expected the actual EP class to be passed.')
        self._name_to_ep[ep.__name__] = ep

        instance.pm = get_weakref(self)
        instances = self._ep_to_context_to_instance.get(ep)
        if instances is None:
            instances = self._ep_to_context_to_instance[ep] = {}
        instances[context] = instance

    def iter_existing_instances(self, ep):
        if ep.__class__ in string_types:
            ep = self._name_to_ep[ep]

        return compat.itervalues(self._ep_to_context_to_instance[ep])

    def has_instance(self, ep, context=None):
        if ep.__class__ in string_types:
            ep = self._name_to_ep.get(ep)
            if ep is None:
                return False

        try:
            self.get_instance(ep, context)
            return True
        except NotRegisteredError:
            return False

    def get_instance(self, ep, context=None):
        '''
        Creates an instance in this plugin manager: Meaning that whenever a new EP is asked in
        the same context it'll receive the same instance created previously (and it'll be
        kept alive in the plugin manager).

        Also, the instance will have its 'pm' attribute set to be this plugin manager.
        '''
        if self.exited:
            raise AssertionError('PluginManager already exited')

        if ep.__class__ in string_types:
            ep = self._name_to_ep[ep]
        try:
            return self._ep_to_context_to_instance[ep][context]
        except KeyError:
            try:
                impls = self._ep_to_instance_impls[(ep, context)]
            except KeyError:
                found = False
                if context is not None:
                    found = True
                    try:
                        impls = self._ep_to_instance_impls[(ep, None)]
                    except KeyError:
                        found = False
                if not found:
                    if ep in self._ep_to_impls:
                        # Registered but not a kept instance.
                        raise NotInstanceError()
                    else:
                        # Not registered at all.
                        raise NotRegisteredError()
            assert len(impls) == 1
            impl, kwargs = impls[0]
            class_ = load_class(impl)

            instances = self._ep_to_context_to_instance.get(ep)
            if instances is None:
                instances = self._ep_to_context_to_instance[ep] = {}

            ret = instances[context] = class_(**kwargs)
            ret.pm = get_weakref(self)
            return ret

    __getitem__ = get_instance

    def exit(self):
        try:
            self.on_about_to_exit()
            for ctx in compat.values(self._ep_to_context_to_instance):
                for instance in compat.values(ctx):
                    if hasattr(instance, 'plugins_exit'):
                        try:
                            instance.plugins_exit()
                        except Exception:
                            import traceback
                            traceback.print_exc()
        finally:
            self.exited = True
            self._ep_to_context_to_instance.clear()
            self._ep_to_impls.clear()


def inject(**inject_kwargs):

    def decorator(func):

        @functools.wraps(func)
        def inject_dec(*args, **kwargs):
            pm = kwargs.get('pm')
            if pm is None:
                raise AssertionError(
                    'pm argument with PluginManager not passed (required for @inject).')

            for key, val in compat.iteritems(inject_kwargs):
                if key not in kwargs:
                    if val.__class__ is list:
                        kwargs[key] = pm.get_implementations(val[0])
                    else:
                        kwargs[key] = pm.get_instance(val)
            return func(*args, **kwargs)

        return inject_dec

    return decorator
