'''
To use:

class MyClassWithResources(Disposable):

    def _on_dispose(self):
        ... # dispose of resources


obj = MyClassWithResources()
...
obj.dispose()
'''


class Disposable(object):
    '''
    Class which warns if it's not properly disposed before object is deleted (which could
    be during interpreter shutdown).
    '''

    def __init__(self):
        import weakref
        self._dispose_info = dispose_info = {'disposed': False}

        s = str(self)

        def on_dispose(ref):
            import sys
            import traceback

            frame = sys._getframe()

            if not dispose_info['disposed']:
                msg = ''.join(traceback.format_list(traceback.extract_stack(frame)) + [
                    '%s: not properly disposed before being collected.\n' % (s,)
                ])
                sys.stderr.write(msg)

        self._ref = weakref.ref(self, on_dispose)

    def dispose(self):
        if not self.is_disposed():
            try:
                self._on_dispose()
            finally:
                self._dispose_info['disposed'] = True

    def is_disposed(self):
        return self._dispose_info['disposed']

    def _on_dispose(self):
        pass
