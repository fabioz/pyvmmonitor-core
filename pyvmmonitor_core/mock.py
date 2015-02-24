# License: LGPL
#
# Copyright: Brainwy Software

'''
A simple mock...
'''


class Mock(object):
    '''
    with Mock(foo, a=10, b=20):
        ...

    or

    mock = Mock(foo, a=10, b=20)
    ...
    mock.__exit__()

    '''

    def __init__(self, obj, **kw):
        '''Create mock object
            obj - Object to be mocked
            kw - Mocked attributes
        '''
        self.obj = obj
        self._restore = []
        for attr, val in kw.iteritems():
            self._restore.append((attr, getattr(obj, attr)))
            setattr(self.obj, attr, val)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        for attr, val in self._restore:
            setattr(self.obj, attr, val)
        self.obj = None
        self._restore = []
