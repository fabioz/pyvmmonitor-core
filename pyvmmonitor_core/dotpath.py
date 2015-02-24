# License: LGPL
#
# Copyright: Brainwy Software


def parent(path):
    index = path.rfind('.')
    if index > -1:
        return path[:index]
    else:
        return ''


def name(path):
    index = path.rfind('.')
    if index > -1:
        return path[index + 1:]
    else:
        return path
