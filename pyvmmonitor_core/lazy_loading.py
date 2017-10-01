# License: LGPL
#
# Copyright: Brainwy Software


def load_token(import_class_path):
    initial = import_class_path
    try:
        i = import_class_path.rindex('.')
        modname = import_class_path[:i]
        import_class_path = import_class_path[i + 1:]

        ret = __import__(modname)
        for part in modname.split('.')[1:]:
            ret = getattr(ret, part)

        ret = getattr(ret, import_class_path)
    except (ImportError, AttributeError):
        raise ImportError('Unable to import: %s' % (initial,))
    return ret


class LazyCallable(object):

    def __init__(self, import_path):
        self.import_path = import_path
        self._loaded = None

    def __call__(self, *args, **kwargs):
        if self._loaded is None:
            self._loaded = load_token(self.import_path)
        return self._loaded(*args, **kwargs)
