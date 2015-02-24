import pytest

from pyvmmonitor_core.system_mutex import SystemMutex
from pyvmmonitor_core.weak_utils import get_weakref


def test_system_mutex():
    mutex_name = 'pyvmmonitor 11111__15'

    system_mutex = SystemMutex(mutex_name)
    assert system_mutex.get_mutex_aquired()

    mutex2 = SystemMutex(mutex_name)
    assert not mutex2.get_mutex_aquired()
    del mutex2

    system_mutex.release_mutex()

    mutex3 = SystemMutex(mutex_name)
    assert mutex3.get_mutex_aquired()
    mutex3 = get_weakref(mutex3)  # Garbage-collected

    # Calling release more times should not be an error
    system_mutex.release_mutex()

    mutex4 = SystemMutex(mutex_name)
    assert mutex4.get_mutex_aquired()

    with pytest.raises(AssertionError):
        SystemMutex('mutex/')  # Invalid name
