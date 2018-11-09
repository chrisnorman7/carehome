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
        'def on_event(self, *args, **kwargs):\n    return (self, args, kwargs)'
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
        'def on_event(self, *args, **kwargs):\n    return (self, args, kwargs)'
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
    p.add_method('def on_init(self):\n    raise InitError()')
    with raises(InitError):
        p.on_init()
    assert 'on_init' in p.methods
    with raises(InitError):
        db.create_object(p)


def test_on_destroy():
    o = db.create_object()
    o.add_method('def on_destroy(self):\n    raise DestroyError()')
    with raises(DestroyError):
        db.destroy_object(o)
    assert o.id in db.objects


def test_on_exit():
    loc = db.create_object()
    loc.add_method('def on_exit(self, thing):\n    self.last_left = thing')
    thing = db.create_object()
    thing.location = loc
    assert not loc.properties
    thing.location = None
    assert loc.last_left is thing
    other = db.create_object()
    other.location = loc
    assert loc.last_left is thing
    other.location = None
    assert loc.last_left is other


def test_on_enter():
    loc = db.create_object()
    loc.add_method('def on_enter(self, thing):\n    self.last_entered = thing')
    assert not loc.properties
    thing = db.create_object()
    thing.location = loc
    assert loc.last_entered is thing
    assert loc.contents == [thing]
    other = db.create_object()
    other.location = loc
    assert loc.last_entered is other
    assert loc.contents == [thing, other]
