def time_method(func):
    '''
    Helper decorator to time a function.

    To use:

    @time_method
    def func():
        ...

    '''
    import time

    try:
        func_name = func.func_name
    except Exception:
        func_name = func.__name__

    def wrap(*args, **kwargs):
        time1 = time.time()
        ret = func(*args, **kwargs)
        print('%s function took %0.3f s' % (func_name, (time.time() - time1)))
        return ret
    return wrap
