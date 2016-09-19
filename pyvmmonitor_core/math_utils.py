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


class Bounds(object):

    x1 = MAX_FLOAT
    y1 = MAX_FLOAT
    x2 = MIN_FLOAT
    y2 = MIN_FLOAT

    def add_point(self, point):
        x, y = point
        if x < self.x1:
            self.x1 = x
        if y < self.y1:
            self.y1 = y

        if x > self.x2:
            self.x2 = x
        if y > self.y2:
            self.y2 = y

    def add_points(self, points):
        for p in points:
            self.add_point(p)

    @property
    def x(self):
        return self.x1

    @property
    def y(self):
        return self.y1

    @property
    def width(self):
        return self.x2 - self.x1

    @property
    def height(self):
        return self.y2 - self.y1

    def is_valid(self):
        return self.x1 <= self.x2 and self.y1 <= self.y2

    @property
    def center(self):
        return ((self.x1 + self.x2) / 2., (self.y1 + self.y2) / 2.)

    @property
    def nodes(self):
        '''
        Returns nodes in the order:

        0 ------------ 3
        |              |
        |              |
        1 ------------ 2
        '''
        return ((self.x1, self.y1), (self.x1, self.y2), (self.x2, self.y2), (self.x2, self.y1))

    def __iter__(self):
        # x, y, w, h
        yield self.x1
        yield self.y1
        yield self.x2 - self.x1
        yield self.y2 - self.y1
