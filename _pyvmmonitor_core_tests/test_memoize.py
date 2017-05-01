def test_memoize():

    import itertools
    count = itertools.count(0)
    from pyvmmonitor_core.memoization import memoize

    @memoize
    def func(param1, param2):
        return [next(count)]

    assert func(1, 2) == [0]
    assert func(1, 2) == [0]
    assert func(1, 2) == [0]
    assert func(1, 4) == [1]
