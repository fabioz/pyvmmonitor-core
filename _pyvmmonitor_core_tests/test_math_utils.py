from pyvmmonitor_core.math_utils import almost_equal


def test_compute_distance():
    from pyvmmonitor_core.math_utils import calculate_distance
    assert almost_equal(calculate_distance((10, 10), (0, 0)), 14.142135623730951)
