'''
To use:

class MyClassWithResources(Disposable):

    def _on_dispose(self):
        ... # dispose of resources


obj = MyClassWithResources()
...
obj.dispose()

If the object isn't properly disposed, a print will be given at interpreter shutdown.
'''
from __future__ import print_function

# This version isn't always correct (when collected during interpreter shutdown it may fail to print).
# class Disposable(object):
#     '''
#     Class which warns if it's not properly disposed before object is deleted (which could
#     be during interpreter shutdown).
#     '''
#
#     def __init__(self):
#         import weakref
#         self._dispose_info = dispose_info = {'disposed': False}
#
#         s = str(self)
#
#         def on_dispose(ref):
#             if not dispose_info['disposed']:
#                 import sys
#                 import traceback
#                 try:
#                     frame = sys._getframe()
#                     lst = traceback.format_list(traceback.extract_stack(frame)[-10:])
#                 finally:
#                     # We can have leaks if we don't collect the frame here.
#                     frame = None
#                 msg = ''.join(lst + [
#                     '%s: not properly disposed before being collected.\n' % (s,)
#                 ])
#                 sys.stderr.write(msg)
#
#         self._ref = weakref.ref(self, on_dispose)
#
#     def dispose(self):
#         if not self.is_disposed():
#             try:
#                 self._on_dispose()
#             finally:
#                 self._dispose_info['disposed'] = True
#
#     def is_disposed(self):
#         return self._dispose_info['disposed']
#
#     def _on_dispose(self):
#         pass


class _Warn(object):

    def __init__(self, msg):
        self.msg = msg

    def __call__(self):
        import sys
        sys.stderr.write(self.msg)


class Disposable(object):
    '''
    Class which warns if it's not properly disposed before object is deleted (which could
    be during interpreter shutdown).
    '''

    def __init__(self):
        self._disposed = False

        try:
            from pyvmmonitor_core import is_development
            if is_development():
                import sys
                import traceback
                frame = sys._getframe()
                lst = traceback.format_list(traceback.extract_stack(frame))
            else:
                lst = []
        finally:
            # We can have leaks if we don't collect the frame here.
            frame = None
        msg = '%s: not properly disposed before being collected (see allocation point above).\n' % (
            self,)
        msg = ''.join(lst + [msg])

        self._msg_callback = _Warn(msg)
        import atexit
        if hasattr(atexit, 'unregister'):
            atexit.register(self._msg_callback)

    def dispose(self):
        import atexit
        if hasattr(atexit, 'unregister'):
            atexit.unregister(self._msg_callback)
        try:
            self._on_dispose()
        finally:
            self._disposed = True

    def is_disposed(self):
        return self._disposed

    def _on_dispose(self):
        pass
