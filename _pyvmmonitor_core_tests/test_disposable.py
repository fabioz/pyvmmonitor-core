

def test_disposable():
    from pyvmmonitor_core import overrides
    from pyvmmonitor_core.disposable import Disposable

    disposed = []

    class MyDisposable(Disposable):

        @overrides(Disposable._on_dispose)
        def _on_dispose(self):
            disposed.append(1)

    d = MyDisposable()
    d.dispose()
    assert disposed == [1]
