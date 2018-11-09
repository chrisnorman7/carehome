"""Test objects."""

from datetime import datetime
from types import MethodType, FunctionType
from pytest import raises
from carehome import Object, Property, Database
from carehome.exc import DuplicateParentError, ParentIsChildError

db = Database()


class CustomObject(Object):
    pass


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
    with raises(DuplicateParentError):
        child.add_parent(child)
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


def test_add_property_invalid():
    o = Object(db)
    with raises(TypeError):
        o.add_property('test1', str, datetime.utcnow())
    with raises(TypeError):
        o.add_property('test2', InvalidType, 'Hello world.')


def test_add_property_null():
    o = Object(db)
    p = o.add_property('location', Object, None)
    assert p.value is None
    assert p.name == 'location'
    assert p.type is Object


def test_add_property_duplicate_name():
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
    o.add_method('def test(self):\n    return self')
    assert o.test() is o


def test_add_method_anonymous():
    o = Object(db)
    with raises(RuntimeError):
        o.add_method(
            'fails', 'return "This will fail because the object is anonymous."'
        )


def test_remove_method():
    o = db.create_object()
    o.add_method('def test(self):\n    return')
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


def test_parents():
    parent_1 = db.create_object()
    parent_2 = db.create_object()
    grandparent_1 = db.create_object()
    o = db.create_object()
    for parent in (parent_1, parent_2):
        o.add_parent(parent)
    assert o.parents == [parent_1, parent_2]
    parent_1.add_parent(grandparent_1)
    assert o.parents == [parent_1, parent_2]


def test_children():
    parent = db.create_object()
    child_1 = db.create_object()
    child_2 = db.create_object()
    for child in (child_1, child_2):
        child.add_parent(parent)
    assert parent.children == [child_1, child_2]
    grandchild_1 = db.create_object()
    grandchild_1.add_parent(child_1)
    assert parent.children == [child_1, child_2]


def test_ancestors():
    grandparent_1 = db.create_object()
    grandparent_2 = db.create_object()
    grandparent_3 = db.create_object()
    grandparent_4 = db.create_object()
    parent_1 = db.create_object()
    parent_2 = db.create_object()
    o = db.create_object()
    assert list(o.ancestors) == []
    for parent in (parent_1, parent_2):
        o.add_parent(parent)
    assert list(o.ancestors) == [parent_1, parent_2]
    for grandparent in (grandparent_1, grandparent_2):
        parent_1.add_parent(grandparent)
    for grandparent in (grandparent_3, grandparent_4):
        parent_2.add_parent(grandparent)
    ancestors = list(o.ancestors)
    assert ancestors == [
        parent_1, grandparent_1, grandparent_2, parent_2, grandparent_3,
        grandparent_4
    ]


def test_descendants():
    grandparent = db.create_object()
    parent_1 = db.create_object()
    parent_2 = db.create_object()
    child_1 = db.create_object()
    child_2 = db.create_object()
    child_3 = db.create_object()
    child_4 = db.create_object()
    assert list(grandparent.descendants) == []
    for parent in (parent_1, parent_2):
        parent.add_parent(grandparent)
    assert list(grandparent.descendants) == [parent_1, parent_2]
    for child in (child_1, child_2):
        child.add_parent(parent_1)
    for child in (child_3, child_4):
        child.add_parent(parent_2)
    descendants = list(grandparent.descendants)
    assert descendants == [
        parent_1, child_1, child_2, parent_2, child_3, child_4
    ]


def test_get_method():
    parent = db.create_object()
    m = parent.add_method('def this(self):\n    return self')
    assert isinstance(m.func, FunctionType)
    assert isinstance(parent.this, MethodType)
    assert parent.this.__self__ is parent
    assert parent.this() is parent
    child = db.create_object()
    child.add_parent(parent)
    assert isinstance(child.this, MethodType)
    assert child.this is not parent.this
    assert child.this.__self__ is child
    assert child.this() is child


def test_method_cache():
    o = db.create_object()
    m = o.add_method('def test(self):\n    return 1')
    assert o.test() == 1
    assert o._method_cache == {id(m.func): o.test}
    o.remove_method('test')
    m = o.add_method('def test(self):\n    return 2')
    assert o.test() == 2
    assert o._method_cache[id(m.func)] is o.test


def test_location():
    loc = db.create_object()
    assert loc.location is None
    assert not loc.contents
    aside = db.create_object(loc)
    assert aside.location is None
    assert not aside.contents
    # Creating a new object shouldn't affect any previously-loaded objects.
    assert loc.location is None
    assert not loc.contents
    thing = db.create_object()
    thing.location = loc
    assert loc.contents == [thing]
    assert thing.location is loc
    assert thing._location == loc.id
    thing.location = None
    assert thing.location is None
    assert not loc.contents


def test_location_custom_object():
    db = Database(object_class=CustomObject)
    loc = db.create_object()
    assert isinstance(loc, CustomObject)
    obj = db.create_object()
    assert isinstance(obj, CustomObject)
    obj.location = loc
    assert obj.location is loc
    assert obj._location == loc.id
    assert loc.contents == [obj]
