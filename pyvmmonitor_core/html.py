'''
Helper for escaping html which works with either bytes or unicode.

License: LGPL

Copyright: Brainwy Software
'''

import sys

PY2 = sys.version_info[0] < 3
PY3 = not PY2

if PY3:

    def escape_html(s, quote=None):
        if isinstance(s, bytes):
            s = s.replace(b"&", b"&amp;")  # First!
            s = s.replace(b"<", b"&lt;")
            s = s.replace(b">", b"&gt;")
            s = s.replace(b'"', b"&quot;")
        else:
            if not isinstance(s, str):
                s = str(s)

            s = s.replace("&", "&amp;")  # First!
            s = s.replace("<", "&lt;")
            s = s.replace(">", "&gt;")
            s = s.replace('"', "&quot;")
        return s

else:

    def escape_html(s, quote=None):
        if isinstance(s, str):
            s = s.replace(b"&", b"&amp;")  # First!
            s = s.replace(b"<", b"&lt;")
            s = s.replace(b">", b"&gt;")
            s = s.replace(b'"', b"&quot;")

        else:
            if not isinstance(s, unicode):
                s = unicode(s)

            s = s.replace(u"&", u"&amp;")  # First!
            s = s.replace(u"<", u"&lt;")
            s = s.replace(u">", u"&gt;")
            s = s.replace(u'"', u"&quot;")

        return s
