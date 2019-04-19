

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
    assert commands_manager.list_active_scopes() == ['default_scope', 'copy_scope']
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
    assert commands_manager.list_active_scopes() == ['default_scope', 'dock_focused']
    commands_manager.activate('copy')
    assert copied == [1, 1, 2]
    commands_manager.deactivate_scope('dock_focused')

    assert commands_manager.list_active_scopes() == ['default_scope']

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
