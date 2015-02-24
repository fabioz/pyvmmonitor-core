# License: LGPL
#
# Copyright: Brainwy Software

import sys

PY2 = sys.version_info[0] < 3
PY3 = not PY2

if PY3:
    def all_basename(name):
        # Instead of using name = os.path.basename(name)
        # use the approach below which is the same on all platforms...
        if isinstance(name, str):
            i = name.rfind('/') + 1
            name = name[i:]
            i = name.rfind('\\') + 1
            name = name[i:]
            return name
        else:
            # unicode
            i = name.rfind(b'/') + 1
            name = name[i:]
            i = name.rfind(b'\\') + 1
            name = name[i:]
            return name

else:
    def all_basename(name):
        # Instead of using name = os.path.basename(name)
        # use the approach below which is the same on all platforms...

        if isinstance(name, unicode):
            i = name.rfind(u'/') + 1
            name = name[i:]
            i = name.rfind(u'\\') + 1
            name = name[i:]
            return name
        else:
            i = name.rfind(b'/') + 1
            name = name[i:]
            i = name.rfind(b'\\') + 1
            name = name[i:]
            return name
