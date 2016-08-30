# License: LGPL
#
# Copyright: Brainwy Software

# Numeric Constants
from math import pow

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
