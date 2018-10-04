"""Test objects."""

from datetime import datetime
from pytest import raises
from carehome import Object, Property, Database
from carehome.exc import DuplicateParentError, ParentIsChildError

db = Database()


class InvalidType:
    pass


def test_creation():
    o = Object(db)
    assert o.database is db
    assert o.id is None
    assert o._properties == {}
    assert o._methods == {}
    assert o._parents == []
    assert o._children == []
    assert o.parents == []
    assert o.children == []


def test_properties():
    o = Object(db)
    o._properties['hello'] = 'world'
    assert o.hello == 'world'
    with raises(AttributeError):
        print(o.test)


def test_add_parent():
    parent = Object(db)
    child = Object(db)
    child.add_parent(parent)
    assert parent in child.parents
    with raises(DuplicateParentError):
        child.add_parent(parent)
    with raises(ParentIsChildError):
        parent.add_parent(child)


def test_properties_inheritance():
    parent = Object(db)
    child = Object(db)
    child.add_parent(parent)
    parent._properties['hello'] = 'world'
    assert child.hello == 'world'
    assert parent.hello == 'world'
    child._properties['hello'] = 'test'
    assert parent.hello == 'world'
    assert child.hello == 'test'


def test_add_property_valid():
    o = Object(db)
    desc = 'Test property'
    value = 'Hello world'
    p = o.add_property('test', str, value, description=desc)
    assert isinstance(p, Property)
    assert p.get() == value
    assert p.type is str
    assert p.description == desc


def test_property_invalid():
    o = Object(db)
    with raises(TypeError):
        o.add_property('test1', str, datetime.utcnow())
    with raises(TypeError):
        o.add_property('test2', InvalidType, 'Hello world.')


def test_property_duplicate_name():
    o = Object(db)
    name = 'test'
    value = 'Hello world.'
    o.add_property(name, str, value)
    with raises(NameError):
        o.add_property(name, type, value)


def test_property_get():
    parent = Object(db)
    value = datetime.utcnow()
    parent.add_property('date', datetime, value)
    assert parent.date is value
    child = Object(db)
    child.add_parent(parent)
    assert child.date is value
    string = '02/10/2018'
    child.add_property('date', str, string)
    assert parent.date is value
    assert child.date == string


def test_add_method():
    o = db.create_object()
    o.add_method('test', 'return self')
    assert o.test() is o


def test_add_method_anonymous():
    o = Object(db)
    with raises(RuntimeError):
        o.add_method(
            'fails', 'return "This will fail because the object is anonymous."'
        )


def test_remove_method():
    o = db.create_object()
    o.add_method('test', 'return')
    assert callable(o.test)
    o.remove_method('test')
    assert not hasattr(o, 'test')


def test_set_id():
    o = db.create_object()
    with raises(RuntimeError):
        o.id = 2


def test_set___initialised__():
    o = db.create_object()
    with raises(RuntimeError):
        o.__initialised__ = None
