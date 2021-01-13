import pytest
from reiter.application import registries


def test_namedcomponents_init():

    reg = registries.NamedComponents()
    assert reg == {}

    reg = registries.NamedComponents({'foo': 'bar'})
    assert reg == {'foo': 'bar'}

    with pytest.raises(TypeError):
        reg = registries.NamedComponents(1)

    with pytest.raises(ValueError):
        reg = registries.NamedComponents('str')


def test_namedcomponents_operator():

    reg = registries.NamedComponents({'foo': 'bar'})
    plugin = registries.NamedComponents({'baz': 'qux'})
    addition = reg + plugin

    assert addition == {'foo': 'bar', 'baz': 'qux'}
    assert reg == {'foo': 'bar'}
    assert plugin == {'baz': 'qux'}

    addition = reg + {'quux': 'corge'}
    assert addition == {'foo': 'bar', 'quux': 'corge'}

    with pytest.raises(TypeError):
        reg + [1]

    with pytest.raises(TypeError):
        reg + 'str'

    with pytest.raises(TypeError):
        reg + {1: "should be a string key"}


def test_namedcomponents_registration():
    reg = registries.NamedComponents()

    @reg.component('test')
    def tester():
        pass

    assert reg == {'test': tester}

    @reg.component('myclass')
    class Tester:
        pass

    assert reg == {'test': tester, 'myclass': Tester}

    @reg.component('test')
    def override_tester():
        pass

    assert reg == {'test': override_tester, 'myclass': Tester}


def test_namedcomponents_registration_errors():
    reg = registries.NamedComponents()

    with pytest.raises(TypeError):
        @reg.component(1)
        def tester():
            pass

    with pytest.raises(TypeError):
        reg[1] = 2

    with pytest.raises(TypeError):
        reg[b'test'] = 1


def test_subscribers():
    reg = registries.Subscribers()

    @reg.subscribe('test')
    def test():
        pass

    assert reg['test'] == test
    assert reg.getall('test') == [test]

    @reg.subscribe('test')
    def test2():
        pass

    assert reg['test'] == test  # always the first
    assert reg.getall('test') == [test, test2]


def test_subscribers_add():
    reg1 = registries.Subscribers()
    reg2 = registries.Subscribers()

    @reg1.subscribe('test')
    def test():
        pass

    @reg2.subscribe('test')
    def test2():
        pass

    reg3 = reg1 + reg2
    assert reg3.getall('test') == [test, test2]


def test_subscribers_notification():
    reg = registries.Subscribers()
    called = []

    @reg.subscribe('test')
    def test():
        called.append('test')

    @reg.subscribe('test')
    def test2():
        called.append('test2')

    reg.notify('test')
    assert called == ['test', 'test2']


def test_subscribers_interruption():
    reg = registries.Subscribers()
    called = []

    @reg.subscribe('test')
    def test():
        called.append('test')
        return True

    @reg.subscribe('test')
    def test2():
        called.append('test2')

    reg.notify('test')
    assert called == ['test']


def test_priority_list():
    reg = registries.PriorityList()
    assert list(reg) == []

    reg = registries.PriorityList(
        [(10, 'test'), (1, 'bar'), (-12, 'foo'), (3, 'qux')])
    list(reg) == [(-12, 'foo'), (1, 'bar'), (3, 'qux'), (10, 'test')]

    assert len(reg) == 4
    assert list(reversed(reg)) == [
        (10, 'test'), (3, 'qux'), (1, 'bar'), (-12, 'foo')]


def test_priority_list_registration():
    reg = registries.PriorityList()
    reg.register('test', 10)
    reg.register('foo', 20)
    reg.register('bar', 5)

    assert list(reg) == [(5, 'bar'), (10, 'test'), (20, 'foo')]

    # if found, it's removed
    reg.unregister('test', 10)
    assert list(reg) == [(5, 'bar'), (20, 'foo')]

    # If not found, nothing happens
    reg.unregister('test', 10)
    assert list(reg) == [(5, 'bar'), (20, 'foo')]

    # Item and order need to both match
    reg.unregister('bar', 15)
    assert list(reg) == [(5, 'bar'), (20, 'foo')]

    # The same item can be registered multiple times
    reg.register('bar', 5)
    assert list(reg) == [(5, 'bar'), (5, 'bar'), (20, 'foo')]

    # Unregistering will remove all instances
    reg.unregister('bar', 5)
    assert list(reg) == [(20, 'foo')]


def test_priority_list_add():
    reg1 = registries.PriorityList([(10, 'test'), (1, 'bar')])
    reg2 = registries.PriorityList([(3, 'qux'), (-12, 'foo')])
    reg3 = reg1 + reg2

    assert list(reg3) == [
        (-12, 'foo'), (1, 'bar'), (3, 'qux'), (10, 'test')
    ]
    assert list(reg1) == [(1, 'bar'), (10, 'test')]
    assert list(reg2) == [(-12, 'foo'), (3, 'qux')]

    with pytest.raises(TypeError) as exc:
        reg1 + ['test']

    str(exc.value) == (
        "unsupported operand type(s) for +: 'PriorityList' and 'list'")
