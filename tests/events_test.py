"""Test the events framework."""

from pytest import raises
from carehome import Database, methods
from carehome.exc import NoSuchEventError

db = Database()


class InitError(Exception):
    pass


class DestroyError(Exception):
    pass


# Make these exceptions accessible to Object methods:
methods.InitError = InitError
methods.DestroyError = DestroyError


def test_valid_event():
    o = db.create_object()
    o.add_method(
        'on_event', 'return (self, args, kwargs)', args='self, *args, **kwargs'
    )
    self, args, kwargs = o.do_event('on_event', 1, 2, 3, hello='world')
    assert self is o
    assert args == (1, 2, 3)
    assert kwargs == {'hello': 'world'}


def test_invalid_event():
    o = db.create_object()
    with raises(NoSuchEventError):
        o.do_event('test_event')


def test_try_event_valid():
    o = db.create_object()
    o.add_method(
        'on_event', 'return (self, args, kwargs)', args='self, *args, **kwargs'
    )
    self, args, kwargs = o.try_event('on_event', 1, 2, 3, hello='world')
    assert self is o
    assert args == (1, 2, 3)
    assert kwargs == {'hello': 'world'}


def test_try_event_invalid():
    o = db.create_object()
    assert o.try_event('test_event') is None


def test_on_init():
    p = db.create_object()
    p.add_method('on_init', 'raise InitError()')
    with raises(InitError):
        p.on_init()
    assert 'on_init' in p.methods
    with raises(InitError):
        db.create_object(p)


def test_on_destroy():
    o = db.create_object()
    o.add_method('on_destroy', 'raise DestroyError()')
    with raises(DestroyError):
        db.destroy_object(o)
    assert o.id in db.objects
