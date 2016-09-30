from pyvmmonitor_core import iterables


def test_iter_curr_and_next():
    lst = [1, 2, 3]
    assert list(iterables.iter_curr_and_next_closed_cycle(lst)) == [
        (1, 2), (2, 3), (3, 1)]
