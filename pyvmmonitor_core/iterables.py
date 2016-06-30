def remove_duplicates(iterable, ret_type=list):
    '''
    Removes duplicate keeping order (and creating a new instance of the returned type).
    '''
    seen = set()
    seen_add = seen.add
    return ret_type(x for x in iterable if not (x in seen or seen_add(x)))


def count_iterable(iterable):
    '''
    Count the number of items in an iterable (note that this will exhaust it in the process and
    it'll be unusable afterwards).
    '''
    i = 0
    for _x in iterable:
        i += 1
    return i
