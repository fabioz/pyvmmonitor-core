from pyvmmonitor_core import overrides
from pyvmmonitor_core.props import PropsCustomProperty, PropsObject


def test_props():

    class MyProps(PropsObject):
        PropsObject.declare_props(a=10)

    p = MyProps()
    assert p.a == 10

    notifications = []

    def on_modified(obj, attrs):
        notifications.append((obj, attrs))

    p.register_modified(on_modified)

    p.a = 20

    assert notifications == [(p, {'a': (20, 10)})]
    p.a = 20
    assert notifications == [(p, {'a': (20, 10)})]

    assert p.create_memento() == {'a': 20}
    p.set_memento({'a': 30})
    assert p.a == 30


def test_custom_props_convert():

    class CustomProp(PropsCustomProperty):

        @overrides(PropsCustomProperty.convert)
        def convert(self, obj, val):
            if val.__class__ == list:
                val = tuple(val)
            return val

    class MyProps(PropsObject):
        PropsObject.declare_props(a=CustomProp((10,)))

    p = MyProps()
    assert p.a == (10,)
    p.a = [20]
    assert p.a == (20,)


def test_props_as_dict():

    class MyProps(PropsObject):
        PropsObject.declare_props(a=10, b=20)

    class MyProps2(MyProps):
        PropsObject.declare_props(c=30)

    props = MyProps2()

    assert props.get_all_props_names() == frozenset(('a', 'b', 'c'))
    props.a = 0
    assert props.get_props_as_dict() == {'a': 0, 'b': 20, 'c': 30}
    assert props.__all_props_cache_info__['hit'] == 1

    assert MyProps2().get_all_props_names() == frozenset(('a', 'b', 'c'))
    assert props.__all_props_cache_info__['hit'] == 2
