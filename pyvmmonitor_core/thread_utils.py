'''
License: LGPL

Copyright: Brainwy Software
'''


def is_in_main_thread():
    import threading
    return threading.currentThread().name == 'MainThread'
