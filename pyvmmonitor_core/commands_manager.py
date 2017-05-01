from pyvmmonitor_core import implements, interface

_DEFAULT_SCOPE = 'default_scope'


class ICommandsManager(object):
    '''
    The commands manager is an API to be used to create commands, bind commands to handlers and
    activate them.

    It's also possible to bind handlers to a given scope so that they're only active when a scope
    is active.

    # The basic usage is:

    commands_manager.register_command('copy')
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

    def register_command(self, command_id):
        '''
        Registers a command and makes it available to be activated (if no handler is available
        after being registered, nothing is done if it's activated).
        '''

    def set_command_handler(self, command_id, command_handler, scope=_DEFAULT_SCOPE):
        '''
        Sets a handler to the given command id (optionally with a different scope).

        The command_handler must be a callable -- it may accept arguments (which then will need to
        be passed in #activate).
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
        self._activated_scopes = [_DEFAULT_SCOPE]
        self._valid_scopes = {_DEFAULT_SCOPE}

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

        if scope == _DEFAULT_SCOPE:
            raise AssertionError('Default scope cannot be deactivated.')

        if not remove_last_occurrence(self._activated_scopes, scope):
            raise RuntimeError(
                'Unable to deactivate scope not activated: %s. Active scopes: %s' %
                (scope, self._activated_scopes))

    @implements(ICommandsManager.register_command)
    def register_command(self, command_id):
        self._command_id_to_scopes[command_id] = {
            _DEFAULT_SCOPE: _default_noop_handler
        }

    @implements(ICommandsManager.set_command_handler)
    def set_command_handler(self, command_id, command_handler, scope=_DEFAULT_SCOPE):
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
