"""Test the events framework."""

from attr import attrs, attrib
from pytest import raises
from carehome import Database, methods
from carehome.exc import NoSuchEventError

db = Database()


@attrs
class Stuff:
    args = attrib()
    kwargs = attrib()


stuff = Stuff(None, None)
methods.stuff = stuff
code = '''def %s(self, *args, **kwargs):
    stuff.args = args
    stuff.kwargs = kwargs
'''


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
    p.add_method(code % 'on_init')
    o = db.create_object(p)
    assert len(stuff.args) == 1
    assert stuff.args[0] is o
    assert stuff.kwargs == {}


def test_on_attach():
    o = db.create_object()
    o.add_method(code % 'on_attach')
    db.attach_object(o)
    assert len(stuff.args) == 1
    assert stuff.args[0]is o
    assert stuff.kwargs == {}


def test_on_destroy():
    o = db.create_object()
    o.add_method(code % 'on_destroy')
    db.destroy_object(o)
    assert len(stuff.args) == 1
    assert stuff.args[0] is o
    assert stuff.kwargs == {}


def test_on_exit():
    loc = db.create_object()
    loc.add_method(
        'def on_exit(self, obj, thing):\n    self.last_left = thing'
    )
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
    loc.add_method(
        'def on_enter(self, obj, thing):\n    self.last_entered = thing'
    )
    assert not loc.properties
    thing = db.create_object()
    thing.location = loc
    assert loc.last_entered is thing
    assert loc.contents == [thing]
    other = db.create_object()
    other.location = loc
    assert loc.last_entered is other
    assert loc.contents == [thing, other]


def test_on_add_parent():
    p = db.create_object()
    c = db.create_object()
    c.add_method(code % 'on_add_parent')
    c.add_parent(p)
    assert len(stuff.args) == 2
    assert stuff.args[0] is c
    assert stuff.args[1] is p
    assert stuff.kwargs == {}


def test_on_add_child():
    p = db.create_object()
    c = db.create_object()
    p.add_method(code % 'on_add_child')
    c.add_parent(p)
    assert len(stuff.args) == 2
    assert stuff.args[0] is p
    assert stuff.args[1] is c
    assert stuff.kwargs == {}


def test_on_remove_parent():
    p = db.create_object()
    c = db.create_object(p)
    c.add_method(code % 'on_remove_parent')
    c.remove_parent(p)
    assert len(stuff.args) == 2
    assert stuff.args[0] is c
    assert stuff.args[1] is p
    assert stuff.kwargs == {}


def test_on_remove_child():
    p = db.create_object()
    p.add_method(code % 'on_remove_child')
    c = db.create_object(p)
    c.remove_parent(p)
    assert len(stuff.args) == 2
    assert stuff.args[0] is p
    assert stuff.args[1] is c
    assert stuff.kwargs == {}


def test_on_add_property():
    o = db.create_object()
    o.add_method(code % 'on_add_property')
    p = o.add_property('test', str, 'Testing.')
    assert len(stuff.args) == 2
    assert stuff.args[0] is o
    assert stuff.args[1] is p
    assert stuff.kwargs == {}


def test_on_remove_property():
    o = db.create_object()
    o.add_method(code % 'on_remove_property')
    name = 'test'
    o.add_property(name, str, 'Testing.')
    o.remove_property(name)
    assert len(stuff.args) == 2
    assert stuff.args[0] is o
    assert stuff.args[1] == name
    assert stuff.kwargs == {}
