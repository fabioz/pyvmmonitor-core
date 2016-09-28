from pyvmmonitor_core import overrides


def test_disposable(capsys):

    from pyvmmonitor_core.disposable import Disposable

    disposed = []

    class MyDisposable(Disposable):

        @overrides(Disposable._on_dispose)
        def _on_dispose(self):
            disposed.append(1)

    d = MyDisposable()
    del d

    out, err = capsys.readouterr()
    assert 'not properly disposed before being collected' in err
    assert out == ''
    assert not disposed

    d = MyDisposable()
    d.dispose()
    del d
    out, err = capsys.readouterr()
    assert out == err == ''
    assert disposed == [1]
