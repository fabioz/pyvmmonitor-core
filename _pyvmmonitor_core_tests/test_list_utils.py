def test_remove_last_occurrence():
    from pyvmmonitor_core.list_utils import remove_last_occurrence
    lst = [1, 2, 3, 3, 2]

    assert remove_last_occurrence(lst, 3)
    assert lst == [1, 2, 3, 2]

    assert remove_last_occurrence(lst, 3)
    assert lst == [1, 2, 2]

    assert not remove_last_occurrence(lst, 3)
    assert lst == [1, 2, 2]
