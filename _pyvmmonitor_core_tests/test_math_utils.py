from pyvmmonitor_core.math_utils import almost_equal, is_clockwise


def test_compute_distance():
    from pyvmmonitor_core.math_utils import calculate_distance
    assert almost_equal(calculate_distance((10, 10), (0, 0)), 14.142135623730951)


def test_is_clockwise():
    assert is_clockwise([(0, 0), (10, 0), (10, 10)])
    assert not is_clockwise([(0, 0), (10, 0), (10, -10)])
