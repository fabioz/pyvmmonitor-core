# License: LGPL
#
# Copyright: Brainwy Software

# Numeric Constants
from math import pow, atan2, cos, sin, sqrt
from pyvmmonitor_core import compat

MAX_INT32 = int(pow(2, 31) - 1)
MIN_INT32 = -(MAX_INT32 + 1)

MAX_UNSIGNED_INT32 = int(pow(2, 32) - 1)

MAX_INT64 = int(pow(2, 63) - 1)
MIN_INT64 = -(MAX_INT32 + 1)

MAX_UNSIGNED_INT64 = int(pow(2, 64) - 1)

MIN_FLOAT = -1e308
MAX_FLOAT = 1e308

PLUS_INFINITY = float('inf')
MINUS_INFINITY = float('-inf')

NAN = float('nan')


def calc_angle_in_radians(p0, p1):
    x1, y1 = p0
    x2, y2 = p1
    theta = atan2(y2 - y1, x2 - x1)
    return theta


def create_point(base_point, angle_in_radians, distance):
    '''
    Creates a new point from an angle and a distance from a base point.
    '''
    x, y = base_point
    x += distance * cos(angle_in_radians)
    y += distance * sin(angle_in_radians)
    return x, y


def calculate_distance(p0, p1):
    return sqrt((p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2)


def almost_equal(v1, v2, delta=1e-7):
    if v1.__class__ in (tuple, list):
        return all(almost_equal(x1, x2, delta) for (x1, x2) in compat.izip(v1, v2))
    return abs(v1 - v2) < delta
