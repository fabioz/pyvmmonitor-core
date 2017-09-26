'''
License: LGPL

Copyright: Brainwy Software

Helpers for dealing with names with dots in it (like os.path deals with slashes).
'''


def parent(path):
    '''
    parent('a.b.c.d') => 'a.b.c'
    parent('foo') => ''
    '''
    index = path.rfind('.')
    if index > -1:
        return path[:index]
    else:
        return ''


def name(path):
    '''
    name('a.b.c.d') => 'd'
    name('foo') => 'foo'
    '''
    index = path.rfind('.')
    if index > -1:
        return path[index + 1:]
    else:
        return path
