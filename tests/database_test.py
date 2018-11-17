"""Test Database objects."""

import re
from datetime import datetime
from types import FunctionType
from pytest import raises
from carehome import Database, Object, Property, Method, ObjectReference
from carehome.exc import LoadPropertyError, LoadMethodError, LoadObjectError


class CustomObject(Object):
    pass


def test_create():
    db = Database()
    assert db.objects == {}
    assert db.max_id == 0
    assert db.method_globals == {'database': db, 'objects': db.objects}
    assert db.methods_dir == 'methods'


def test_create_object():
    db = Database()
    o1 = db.create_object()
    assert isinstance(o1, Object)
    assert o1.database is db
    assert o1.id == 0
    assert db.max_id == 1
    assert db.objects == {0: o1}
    o2 = db.create_object()
    assert isinstance(o2, Object)
    assert o2.database is db
    assert o2.id == 1
    assert db.max_id == 2
    assert db.objects == {0: o1, 1: o2}


def test_destroy_object():
    db = Database()
    o = db.create_object()
    db.destroy_object(o)
    assert db.objects == {}
    o1 = db.create_object()
    o2 = db.create_object()
    db.destroy_object(o2)
    assert o1.id == 1
    assert db.objects == {1: o1}
    assert db.max_id == 3


def test_destroy_object_with_parents():
    d = Database()
    g = d.create_object()
    p = d.create_object(g)
    # I know we've done these inheritence tests elsewhere, I just feel more
    # secure knowing they're in two separate places.
    assert g.children == [p]
    assert p.parents == [g]
    c = d.create_object(p)
    assert c.parents == [p]
    assert p.children == [c]
    d.destroy_object(c)
    assert not p.children
    assert g.children == [p]


def test_destroy_object_registered():
    d = Database()
    first = d.create_object()
    d.register_object('first', first)
    second = d.create_object()
    d.register_object('second', second)
    d.destroy_object(first)
    assert d.registered_objects == dict(second=second)


def test_dump_property():
    d = Database()
    name = 'test'
    desc = 'Test property.'
    type = str
    value = 'Test string.'
    p = Property(name, desc, type, value)
    actual = d.dump_property(p)
    expected = dict(name=name, description=desc, value=value, type='str')
    assert expected == actual
    p.type = Exception
    with raises(RuntimeError):
        d.dump_property(p)


def test_load_property():
    d = Database()
    o = d.create_object()
    name = 'test'
    desc = 'Test date.'
    value = datetime.utcnow()
    p = d.load_property(
        o, dict(name=name, type='datetime', value=value, description=desc)
    )
    assert p.value == value
    assert p.type is datetime
    assert p.description == desc
    assert o._properties[p.name] is p


def test_load_property_malformed():
    d = Database()
    o = d.create_object()
    with raises(LoadPropertyError) as err:
        d.load_property(o, d)
    assert err.value.args[0] is o
    assert err.value.args[1] is d
    assert isinstance(err.value.__cause__, TypeError)


def test_dump_method():
    d = Database()
    name = 'test'
    code = 'def %s(self):\n    return 1234' % name
    m = Method(d, code)
    actual = d.dump_method(m)
    expected = dict(name=name, code=code)
    assert actual == expected


def test_load_method():
    d = Database()
    o = d.create_object()
    name = 'test'
    code = 'import re\ndef %s(self, a, b):\n    return (a, b, re)' % name
    m = d.load_method(o, dict(name=name, code=code))
    assert isinstance(m, Method)
    assert o._methods[name] is m
    assert m.database is d
    assert m.name == name
    assert isinstance(m.func, FunctionType)
    assert m.code == code
    assert m.func(o, 1, 2) == (1, 2, re)


def load_method_malformed():
    d = Database()
    o = d.create_object()
    with raises(LoadMethodError) as err:
        d.load_metod(o, d)
    assert err.value.args[0] is o
    assert err.value.args[1] is d
    assert isinstance(err.value.__cause__, TypeError)


def test_dump_object():
    d = Database()
    parent_1 = d.create_object()
    parent_2 = d.create_object()
    assert d.dump_object(parent_1) == dict(
        location=None, id=parent_1.id, parents=[], properties=[], methods=[]
    )
    o = d.create_object()
    for parent in (parent_1, parent_2):
        o.add_parent(parent)
    actual = d.dump_object(o)
    expected = dict(
        location=None, id=o.id, properties=[], methods=[],
        parents=[parent_1.id, parent_2.id]
    )
    assert actual == expected
    parent_2.location = parent_1
    res = d.dump_object(parent_2)
    assert 'location' not in res['properties']
    assert res['location'] == parent_1.id


def test_load_object():
    d = Database()
    id = 18
    p = Property('property', 'Test property.', bool, False)
    m = Method(d, 'import re\ndef method(self, a, b):\n    return (a, b, re)')
    data = dict(
        id=id, methods=[d.dump_method(m)], properties=[d.dump_property(p)],
        parents=[]
    )
    o = d.load_object(data)
    assert d.objects[id] is o
    assert d.max_id == (id + 1)
    assert len(o._methods) == 1
    m.func = None
    for method in (m, o._methods[m.name]):
        method.created.clear()
    o._methods[m.name].func = None  # Otherwise they'll never match.
    assert o._methods[m.name] == m
    assert not o._properties
    assert not o._parents
    assert not o._children
    data = dict(id=1, location=2)
    o = d.load_object(data)
    assert o._location == 2


def test_load_object_malformed():
    d = Database()
    with raises(LoadObjectError) as err:
        d.load_object(d)
    assert err.value.args[0] is d
    assert isinstance(err.value.__cause__, AttributeError)


def test_dump():
    d = Database()
    o1 = d.create_object()
    o2 = d.create_object()
    name = 'test'
    d.register_object(name, o1)
    data = d.dump()
    assert data['registered_objects'] == {name: o1.id}
    assert len(data['objects']) == 2
    assert data['objects'][0]['id'] == o1.id
    assert data['objects'][1]['id'] == o2.id


def test_load():
    d = Database()
    grandparent_1 = d.create_object()
    grandparent_2 = d.create_object()
    parent = d.create_object()
    for grandparent in (grandparent_1, grandparent_2):
        parent.add_parent(grandparent)
    child = d.create_object()
    child.add_parent(parent)
    for name, obj in (
        ('grandparent_1', grandparent_1), ('grandparent_2', grandparent_2),
        ('parent', parent), ('child', child)
    ):
        d.register_object(name, obj)
    data = d.dump()
    new = Database()
    new.load(data)
    assert d.child.id == child.id
    assert d.parent.id == parent.id
    assert d.child._parents == [d.parent]
    assert d.grandparent_1.id == grandparent_1.id
    assert d.grandparent_2.id == grandparent_2.id
    assert d.parent._parents == [d.grandparent_1, d.grandparent_2]


def test_register_object():
    d = Database()
    o = d.create_object()
    name = 'test'
    d.register_object(name, o)
    assert d.registered_objects == {name: o}
    assert d.test is o
    o = Object(d)
    with raises(RuntimeError):
        d.register_object(name, o)


def test_unregister_object():
    d = Database()
    o = d.create_object()
    name = 'test'
    d.register_object(name, o)
    d.unregister_object(name)
    assert not d.registered_objects
    with raises(AttributeError):
        print(d.test)
    with raises(KeyError):
        d.unregister_object(name)


def test_dump_objectreference():
    d = Database()
    f1 = d.create_object()
    f2 = d.create_object()
    o = d.create_object()
    p = o.add_property('friends', list, [f1, f2])
    assert p.value == [f1, f2]
    data = d.dump_property(p)
    for entry in data['value']:
        assert isinstance(entry, ObjectReference), 'Invalid entry: %r.' % entry
    assert data['value'] == [ObjectReference(f1.id), ObjectReference(f2.id)]


def test_dump_value():
    d = Database()
    o1 = d.create_object()
    o2 = d.create_object()
    data = dict(names=['hello', 'world'], age=25, objects=[o1, o2])
    res = d.dump_value(data)
    assert res == dict(
        names=['hello', 'world'], age=25, objects=[
            ObjectReference(o1.id), ObjectReference(o2.id)
        ]
    )


def test_load_value():
    d = Database()
    o1 = d.create_object()
    o2 = d.create_object()
    data = dict(
        names=['hello', 'world'], objects=[
            ObjectReference(o1.id), ObjectReference(o2.id)
        ], age=29
    )
    value = d.load_value(data)
    assert value == dict(
        names=['hello', 'world'], objects=[o1, o2], age=29
    )


def test_custom_object():
    d = Database(object_class=CustomObject)
    o = d.create_object()
    assert isinstance(o, d.object_class)
    o = d.load_object(dict(id=1, methods=[]))
    assert isinstance(o, CustomObject)


def test_dump_value_object_class():
    d = Database(object_class=CustomObject)
    o = d.create_object()
    value = d.dump_value(o)
    assert isinstance(value, ObjectReference)


def test_load_value_object_class():
    d = Database(object_class=CustomObject)
    o = d.create_object()
    assert isinstance(o, CustomObject)
    value = d.load_value(ObjectReference(o.id))
    assert value is o


def test_clear_func_cache():
    d = Database()
    parent = d.create_object()
    parent.add_method('def test1(self):\n    return 1')
    child = d.create_object()
    child.add_method('def test2(self):\n    return 2')
    child.add_parent(parent)
    parent.test1()
    assert len(parent._method_cache) == 1
    child.test1()
    child.test2()
    assert len(child._method_cache) == 2
    d.clear_method_cache()
    assert not parent._method_cache
    assert not child._method_cache


def test_create_object_with_parents():
    d = Database()
    parent_1 = d.create_object()
    parent_2 = d.create_object()
    child = d.create_object(parent_1, parent_2)
    assert not parent_1.parents
    assert not parent_2.parents
    assert child.parents == [parent_1, parent_2]


def test_property_types():
    d = Database()
    assert d.property_types['obj'] is Object
    d = Database(object_class=CustomObject)
    assert d.property_types['obj'] is CustomObject
    o = d.create_object()
    o.this = o
    assert o._properties['this'].type is d.object_class


def test_dump_property_custom_object():
    d = Database(object_class=CustomObject)
    o = d.create_object()
    p = o.add_property('this', d.object_class, o)
    value = d.dump_property(p)
    assert value['type'] == 'obj'
