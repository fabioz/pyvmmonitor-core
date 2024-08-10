'''
License: LGPL

Copyright: Brainwy Software
'''


def is_in_main_thread():
    import threading
    return threading.current_thread().name == 'MainThread'
