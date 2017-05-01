# License: LGPL
#
# Copyright: Brainwy Software


def remove_last_occurrence(lst, element):
    '''
    Removes the last occurrence of a given element in a list (modifies list in-place).

    :return bool:
        True if the element was found and False otherwise.
    '''
    for i, s in enumerate(reversed(lst)):
        if s == element:
            del lst[len(lst) - 1 - i]
            return True
    return False
