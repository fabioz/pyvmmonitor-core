'''
Helpers for debugging:

To use:

set_magic_var()

...

Somewhere else in the code:

if is_magic_var_set():
    import pydevd;pydevd.settrace()

License: LGPL
Copyright: Brainwy Software
'''

_magic_vars = {}


def set_magic_var(var_name='global_var', value=1):
    _magic_vars[var_name] = value


def inc_magic_var(var_name='global_var'):
    _magic_vars[var_name] = _magic_vars.get(var_name, 0) + 1


def is_magic_var_set(var_name='global_var'):
    return _magic_vars.get(var_name) is not None


def get_magic_var(var_name='global_var'):
    return _magic_vars.get(var_name)
