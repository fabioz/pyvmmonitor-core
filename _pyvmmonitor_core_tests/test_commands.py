from pyvmmonitor_core.commands_manager import ICommandsManager


def test_commands_params():
    from pyvmmonitor_core.commands_manager import create_default_commands_manager

    copied = []

    def dummy_copy(param):
        copied.append(param)

    commands_manager = create_default_commands_manager()
    commands_manager.register_command('copy', 'Copy')
    commands_manager.activate('copy', param=2)
    assert copied == []  # Default handler does nothing

    commands_manager.set_command_handler('copy', dummy_copy)
    commands_manager.activate('copy', param=2)
    assert copied == [2]


def test_scope_activate():
    from pyvmmonitor_core.commands_manager import create_default_commands_manager
    from pyvmmonitor_core.commands_manager import ICommandsManager

    copied = []

    def dummy_bar():
        copied.append('bar')

    def dummy_foo():
        copied.append('foo')

    commands_manager = create_default_commands_manager()
    commands_manager.register_command('copy', 'Copy')
    commands_manager.register_scope('scope1')
    commands_manager.set_command_handler('copy', dummy_bar)
    commands_manager.set_command_handler('copy', dummy_foo, scope='scope1')

    commands_manager.activate('copy')
    assert copied == ['bar']

    commands_manager.activate('copy', 'scope1')
    assert copied == ['bar', 'foo']

    commands_manager.activate_scope('scope1')

    commands_manager.activate('copy')
    assert copied == ['bar', 'foo', 'foo']

    commands_manager.activate('copy', ICommandsManager.DEFAULT_SCOPE)
    assert copied == ['bar', 'foo', 'foo', 'bar']


def test_commands_remove_handler():
    from pyvmmonitor_core.commands_manager import create_default_commands_manager

    copied = []

    def dummy_copy():
        copied.append(1)

    def dummy_foo():
        print

    commands_manager = create_default_commands_manager()
    commands_manager.register_command('copy', 'Copy')
    commands_manager.activate('copy')
    assert copied == []

    commands_manager.register_scope('copy_scope')
    commands_manager.set_command_handler('copy', dummy_copy, scope='copy_scope')
    commands_manager.activate('copy')
    assert copied == []

    commands_manager.activate_scope('copy_scope')
    assert commands_manager.list_active_scopes() == [ICommandsManager.DEFAULT_SCOPE, 'copy_scope']
    commands_manager.activate('copy')
    assert copied == [1]

    # Don't remove because it's not the current one.
    commands_manager.remove_command_handler('copy', dummy_foo, scope='copy_scope')
    commands_manager.activate('copy')
    assert copied == [1, 1]

    # Now, actually remove it.
    commands_manager.remove_command_handler('copy', dummy_copy, scope='copy_scope')
    commands_manager.activate('copy')
    assert copied == [1, 1]


def test_commands():
    from pyvmmonitor_core.commands_manager import CommandUndefinedEror
    from pyvmmonitor_core.commands_manager import create_default_commands_manager
    import pytest

    copied = []

    def dummy_copy():
        copied.append(1)

    def dummy_copy_on_dock_focused():
        copied.append(2)

    commands_manager = create_default_commands_manager()
    commands_manager.register_command('copy', 'Copy')
    commands_manager.activate('copy')
    assert copied == []

    commands_manager.set_command_handler('copy', dummy_copy)

    commands_manager.activate('copy')
    assert copied == [1]

    # Allow to override commands in a given scope
    commands_manager.register_scope('dock_focused')
    commands_manager.set_command_handler('copy', dummy_copy_on_dock_focused, scope='dock_focused')
    commands_manager.activate('copy')
    assert copied == [1, 1]

    commands_manager.activate_scope('dock_focused')
    assert commands_manager.list_active_scopes() == [ICommandsManager.DEFAULT_SCOPE, 'dock_focused']
    commands_manager.activate('copy')
    assert copied == [1, 1, 2]
    commands_manager.deactivate_scope('dock_focused')

    assert commands_manager.list_active_scopes() == [ICommandsManager.DEFAULT_SCOPE]

    commands_manager.activate('copy')
    assert copied == [1, 1, 2, 1]

    with pytest.raises(RuntimeError):
        commands_manager.deactivate_scope('dock_focused')

    with pytest.raises(ValueError):
        commands_manager.activate_scope('invalid')

    with pytest.raises(ValueError):
        commands_manager.set_command_handler('copy', dummy_copy_on_dock_focused, scope='invalid')

    with pytest.raises(CommandUndefinedEror):
        commands_manager.activate('invalid')

    with pytest.raises(RuntimeError):
        commands_manager.register_command('copy', 'Foo')

    assert commands_manager.list_command_ids() == ['copy']
