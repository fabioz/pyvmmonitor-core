'''
The commands manager is an API to be used to create commands, bind commands to handlers and
activate them.

It's also possible to bind handlers to a given scope so that they're only active when a scope
is active.

# The basic usage is:

commands_manager.register_command('copy', 'Copy')
commands_manager.set_command_handler('copy', copy_to_clipboard)
commands_manager.activate('copy')  # activates the copy action

# Then, if there was a special copy on some context,
# one would need to register the scope/handler:

commands_manager.register_scope('custom_scope')
commands_manager.set_command_handler('copy', copy_to_clipboard, 'custom_scope')

# And then active/deactivate such a context when needed:

commands_manager.activate_scope('custom_scope')
commands_manager.activate('copy')
commands_manager.deactivate_scope('custom_scope')
'''

from collections import namedtuple

from pyvmmonitor_core import implements, interface


class ICommandsManager(object):

    DEFAULT_SCOPE = 'default_scope'

    def register_command(self, command_id, command_name, icon=None, status_tip=None):
        '''
        Registers a command and makes it available to be activated (if no handler is available
        after being registered, nothing is done if it's activated).

        :param str command_id:
        :param str command_name:
        :param object icon:
            May be the actual icon or a way to identify it (at core it doesn't make
            a difference, it just stores the value to be consumed later on).
        :param str status_tip:
            A tip for the command (if not given, a default one may be given based on the
            command_name).
        '''

    def get_command_info(self, command_id):
        '''
        :param str command_id:
            The command id for which we want the info.

        :return: a namedtuple with command_id, command_name, icon, status_tip
        '''

    def set_command_handler(self, command_id, command_handler, scope=DEFAULT_SCOPE):
        '''
        Sets a handler to the given command id (optionally with a different scope).

        The command_handler must be a callable -- it may accept arguments (which then will need to
        be passed in #activate).

        It's possible to pass None to set no command handler in the context (also see
        remove_command_handler to remove a registered command handler -- in case it's registered
        and then removed).
        '''

    def remove_command_handler(self, command_id, command_handler, scope=DEFAULT_SCOPE):
        '''
        Removes a registered handler if it's the current handler at a given scope (does nothing
        if it's not the current handler).
        '''

    def activate(self, command_id, **kwargs):
        '''
        Activates a given command.

        kwargs are passed on to the handler of the command. Note that only arguments which are
        simple python objects should be passed.

        Namely: int/long/float/complex/str/bytes/bool/tuple/list/set (this restriction is enforced
        so that clients can be sure that they can easily replicate a command invocation).
        '''

    def register_scope(self, scope):
        '''
        :param str scope:
            The scope which can have a different set of handlers for the existing actions.
        '''

    def activate_scope(self, scope):
        '''
        Activates a given scope so that the commands registered in such a scope have precedence
        over the commands in the default scope (or previously activated scopes).
        '''

    def deactivate_scope(self, scope):
        '''
        Deactivates a previously activated scope.
        '''

    def list_command_ids(self):
        '''
        Returns the available command ids.
        '''

    def list_active_scopes(self):
        '''
        Returns the current scope activation list.

        :rtype: list(str)
        '''


def create_default_commands_manager():
    '''
    Creates a default implementation for ICommandsManager.
    '''
    return _DefaultCommandsManager()

# --- Private API from now on ---


def _default_noop_handler(**kwargs):
    pass


class CommandUndefinedEror(Exception):
    pass


_CommandInfo = namedtuple('_CommandInfo', ('command_id', 'command_name', 'icon', 'status_tip'))


@interface.check_implements(ICommandsManager)
class _DefaultCommandsManager(object):
    '''
    Users should base on ICommandsManager (create_default_commands_manager can be used to create
    a default implementation, this class is not exposed and can be removed -- use aggregation
    to compose a new class if needed).

    @see: create_default_commands_manager()
    '''

    def __init__(self):
        self._command_id_to_scopes = {}
        self._command_id_to_info = {}
        self._activated_scopes = [ICommandsManager.DEFAULT_SCOPE]
        self._valid_scopes = {ICommandsManager.DEFAULT_SCOPE}

    @implements(ICommandsManager.list_command_ids)
    def list_command_ids(self):
        from pyvmmonitor_core import compat
        return compat.keys(self._command_id_to_info)

    @implements(ICommandsManager.list_active_scopes)
    def list_active_scopes(self):
        return self._activated_scopes[:]

    @implements(ICommandsManager.register_scope)
    def register_scope(self, scope):
        self._valid_scopes.add(scope)

    @implements(ICommandsManager.activate_scope)
    def activate_scope(self, scope):
        if scope not in self._valid_scopes:
            raise ValueError('The passed scope (%s) was not registered.' % (scope,))

        self._activated_scopes.append(scope)

        if len(self._activated_scopes) > 20:
            import sys
            sys.stderr.write(
                'It seems there is some issue in scopes not being deactivated!\nActivated scopes: %s' %  # @IgnorePep8
                (self._activated_scopes,))

    @implements(ICommandsManager.deactivate_scope)
    def deactivate_scope(self, scope):
        from pyvmmonitor_core.list_utils import remove_last_occurrence

        if scope == ICommandsManager.DEFAULT_SCOPE:
            raise AssertionError('Default scope cannot be deactivated.')

        if not remove_last_occurrence(self._activated_scopes, scope):
            raise RuntimeError(
                'Unable to deactivate scope not activated: %s. Active scopes: %s' %
                (scope, self._activated_scopes))

    @implements(ICommandsManager.register_command)
    def register_command(self, command_id, command_name, icon=None, status_tip=None):
        if command_id in self._command_id_to_info:
            raise RuntimeError('Command: %s already registered' % (command_id,))

        self._command_id_to_info[command_id] = _CommandInfo(
            command_id, command_name, icon, status_tip)

        self._command_id_to_scopes[command_id] = {
            ICommandsManager.DEFAULT_SCOPE: _default_noop_handler
        }

    @implements(ICommandsManager.get_command_info)
    def get_command_info(self, command_id):
        try:
            return self._command_id_to_info[command_id]
        except KeyError:
            raise CommandUndefinedEror('Command with id: %s is not defined.' % (command_id,))

    @implements(ICommandsManager.set_command_handler)
    def set_command_handler(self, command_id, command_handler,
                            scope=ICommandsManager.DEFAULT_SCOPE):
        if scope not in self._valid_scopes:
            raise ValueError('The passed scope (%s) was not registered.' % (scope,))

        try:
            scopes = self._command_id_to_scopes[command_id]
        except KeyError:
            raise CommandUndefinedEror('Command with id: %s is not defined.' % (command_id,))
        else:
            prev_command_handler = scopes.get(scope, _default_noop_handler)
            scopes[scope] = command_handler
            return prev_command_handler

    @implements(ICommandsManager.remove_command_handler)
    def remove_command_handler(self, command_id, command_handler,
                               scope=ICommandsManager.DEFAULT_SCOPE):
        if scope not in self._valid_scopes:
            raise ValueError('The passed scope (%s) was not registered.' % (scope,))

        try:
            scopes = self._command_id_to_scopes[command_id]
        except KeyError:
            raise CommandUndefinedEror('Command with id: %s is not defined.' % (command_id,))
        else:
            prev_command_handler = scopes.get(scope, _default_noop_handler)
            if prev_command_handler is command_handler:
                scopes[scope] = None
            return True

    @implements(ICommandsManager.activate)
    def activate(self, command_id, **kwargs):
        try:
            scopes = self._command_id_to_scopes[command_id]
        except KeyError:
            raise CommandUndefinedEror('Command with id: %s is not defined.' % (command_id,))
        else:
            for active_scope in reversed(self._activated_scopes):
                handler = scopes.get(active_scope)
                if handler is not None:
                    handler(**kwargs)
                    break
