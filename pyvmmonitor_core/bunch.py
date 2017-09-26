'''
To use a Bunch do:

bunch = Bunch(a=10, b=20)
print(bunch.a)
'''


class Bunch(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
