class ISomething(object):

    def m1(self, a, *, b=10):
        pass


class SomethingImpl(object):

    def m1(self, a, *, b=10):
        pass


class SomethingImplWrong(object):

    def m1(self, a, *, b=5):
        pass
