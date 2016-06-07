def remove_duplicates(iterable, ret_type=list):
    '''
    Removes duplicate keeping order (and creating a new instance of the returned type).
    '''
    seen = set()
    seen_add = seen.add
    return ret_type(x for x in iterable if not (x in seen or seen_add(x)))
