def test_bounds():
    from pyvmmonitor_core.math_utils import Bounds
    bounds = Bounds()
    assert not bounds.is_valid()
    bounds.add_point((10, 10))

    assert bounds.is_valid()
    assert bounds.width == 0
    assert bounds.height == 0

    bounds.add_point((0, 0))
    assert bounds.nodes == ((0, 0), (0, 10), (10, 10), (10, 0))
    assert bounds.width == 10
    assert bounds.height == 10

    assert bounds.center == (5, 5)

    x, y, w, h = bounds
    assert (x, y, w, h) == (0, 0, 10, 10)
