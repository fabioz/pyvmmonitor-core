# License: LGPL
#
# Copyright: Brainwy Software

from pyvmmonitor_core.callback import Callback
from pyvmmonitor_core.weak_utils import get_weakref


def load_class(import_class_path):
    i = import_class_path.rindex('.')
    modname = import_class_path[:i]
    import_class_path = import_class_path[i + 1:]

    ret = __import__(modname)
    for part in modname.split('.')[1:]:
        ret = getattr(ret, part)

    ret = getattr(ret, import_class_path)
    return ret


class NotInstanceError(RuntimeError):
    pass


class NotRegisteredError(RuntimeError):
    pass


class InstanceAlreadyRegisteredError(RuntimeError):
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
        self._ep_and_context_to_instance = {}
        self.exited = False
        self.on_about_to_exit = Callback()

    def get_implementations(self, ep):
        assert not self.exited
        impls = self._ep_to_impls.get(ep, [])
        ret = []
        for impl, kwargs in impls:
            class_ = load_class(impl)
            instance = class_(**kwargs)
            instance.pm = get_weakref(self)
            ret.append(instance)

        return ret

    def register(self, ep, impl, kwargs={}, keep_instance=False):
        '''

        :param ep:
        :param str impl:
            This is the full path to the class implementation.

        :param kwargs:
        :param keep_instance:
            If True, it'll be only available through pm.get_instance and the
            instance will be kept for further calls.
            If False, it'll only be available through get_implementations.
        '''
        assert not self.exited
        if keep_instance:
            register_at = self._ep_to_instance_impls
            impls = register_at.get(ep)
            if impls is None:
                impls = register_at[ep] = []
            else:
                raise InstanceAlreadyRegisteredError(
                    'Unable to override when instance is kept and an implementation is already registered.')
        else:
            register_at = self._ep_to_impls
            impls = register_at.get(ep)
            if impls is None:
                impls = register_at[ep] = []

        impls.append((impl, kwargs))

    def set_instance(self, ep, instance, context=None):
        key = (ep, context)
        instance.pm = get_weakref(self)
        self._ep_and_context_to_instance[key] = instance

    def get_instance(self, ep, context=None):
        '''
        Creates an instance in this plugin manager: Meaning that whenever a new EP is asked in
        the same context it'll receive the same instance created previously (and it'll be
        kept alive in the plugin manager).

        Also, the instance will have its 'pm' attribute set to be this plugin manager.
        '''
        assert not self.exited
        key = (ep, context)
        try:
            return self._ep_and_context_to_instance[key]
        except:
            try:
                impls = self._ep_to_instance_impls[ep]
            except KeyError:
                if ep in self._ep_to_impls:
                    # Registered but not a kept instance.
                    raise NotInstanceError()
                else:
                    # Not registered at all.
                    raise NotRegisteredError()
            assert len(impls) == 1
            impl, kwargs = impls[0]
            class_ = load_class(impl)
            ret = self._ep_and_context_to_instance[key] = class_(**kwargs)
            ret.pm = get_weakref(self)
            return ret

    def exit(self):
        try:
            self.on_about_to_exit()
            for instance in list(self._ep_and_context_to_instance.values()):
                if hasattr(instance, 'plugins_exit'):
                    try:
                        instance.plugins_exit()
                    except:
                        import traceback
                        traceback.print_exc()
        finally:
            self.exited = True
            self._ep_and_context_to_instance.clear()
            self._ep_to_impls.clear()
