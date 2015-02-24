# License: LGPL
#
# Copyright: Brainwy Software

from pyvmmonitor_core.callback import Callback
from pyvmmonitor_core.weak_utils import get_weakref


def _get_class(classname):
    i = classname.rindex('.')
    modname = classname[:i]
    classname = classname[i + 1:]

    ret = __import__(modname)
    for part in modname.split('.')[1:]:
        ret = getattr(ret, part)

    ret = getattr(ret, classname)
    return ret


class NotSingletonError(RuntimeError):
    pass


class NotRegisteredError(RuntimeError):
    pass


class PluginManager(object):

    '''
    This is a manager of plugins.

    Mostly, we have a number of EPs (Extension Points) and implementations may be registered
    for those extension points.

    The PluginManager is able to provide implementations (through #get_impls) which are not
    kept on being tracked and a special concept which keeps an instance alive for an extension
    (through #get_singleton) -- note that it's not a real singleton, but rather a single instance
    that's registered for some implementation.

    Every singleton registered will have a 'plugins_exit' method called if it defines it when
    the PluginManager is about to exit.
    '''

    def __init__(self):
        self._ep_to_impls = {}
        self._ep_to_singleton_impls = {}
        self._ep_and_context_to_singleton = {}
        self.exited = False
        self.on_about_to_exit = Callback()

    def get_impls(self, ep):
        assert not self.exited
        impls = self._ep_to_impls.get(ep, [])
        ret = []
        for impl, kwargs in impls:
            class_ = _get_class(impl)
            ret.append(class_(**kwargs))

        return ret

    def register(self, ep, impl, kwargs={}, singleton=False):
        assert not self.exited
        if singleton:
            register_at = self._ep_to_singleton_impls
        else:
            register_at = self._ep_to_impls
        impls = register_at.get(ep)
        if impls is None:
            impls = register_at[ep] = []
        impls.append((impl, kwargs))

    def set_singleton(self, ep, instance, context=None):
        key = (ep, context)
        instance.pm = get_weakref(self)
        self._ep_and_context_to_singleton[key] = instance

    def get_singleton(self, ep, context=None):
        '''
        Creates a singleton in this plugin manager: Meaning that whenever a new EP is asked in
        the same context it'll receive the same instance created previously (and it'll be
        kept alive in the plugin manager).

        Also, the singleton has its 'pm' attribute set to be this plugin manager.
        '''
        assert not self.exited
        key = (ep, context)
        try:
            return self._ep_and_context_to_singleton[key]
        except:
            try:
                impls = self._ep_to_singleton_impls[ep]
            except KeyError:
                if ep in self._ep_to_impls:
                    # Registered but not a singleton.
                    raise NotSingletonError()
                else:
                    # Not registered at all.
                    raise NotRegisteredError()
            assert len(impls) == 1
            impl, kwargs = impls[0]
            class_ = _get_class(impl)
            ret = self._ep_and_context_to_singleton[key] = class_(**kwargs)
            ret.pm = get_weakref(self)
            return ret

    def exit(self):
        try:
            self.on_about_to_exit()
            for singleton in list(self._ep_and_context_to_singleton.itervalues()):
                if hasattr(singleton, 'plugins_exit'):
                    try:
                        singleton.plugins_exit()
                    except:
                        import traceback
                        traceback.print_exc()
        finally:
            self.exited = True
            self._ep_and_context_to_singleton.clear()
            self._ep_to_impls.clear()
