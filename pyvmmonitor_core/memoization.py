def memoize(function):
    '''
    Use as:

    @memoize
    def method(v1):
        pass

    Note that memoizes everything passed (things put in it will never be collected).
    '''
    from functools import wraps

    memo = {}

    @wraps(function)
    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            ret = function(*args)
            memo[args] = ret
            return ret

    return wrapper
