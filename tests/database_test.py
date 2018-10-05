"""Test Database objects."""

import re
from datetime import datetime
from pytest import raises
from carehome import Database, Object, Property, Method
from carehome.exc import CantLoadYetError


def test_create():
    db = Database()
    assert db.objects == {}
    assert db.max_id == 0


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


def test_dump_method():
    d = Database()
    name = 'test'
    description = 'Test method for dumping.'
    args = ''
    imports = []
    code = 'return 1234'
    m = Method(d, name, description, args, imports, code)
    actual = d.dump_method(m)
    expected = dict(
        name=name, description=description, args=args, imports=imports,
        code=code
    )
    assert actual == expected


def test_load_method():
    d = Database()
    o = d.create_object()
    name = 'test'
    description = 'This is a test function.'
    args = 'a, b'
    imports = ['import re']
    code = 'return (a, b, re)'
    m = d.load_method(
        o, dict(
            name=name, description=description, args=args, imports=imports,
            code=code
        )
    )
    assert isinstance(m, Method)
    assert o._methods[name] is m
    assert m.database is d
    assert m.name == name
    assert m.description == description
    assert m.args == args
    assert m.imports == imports
    code = 'self = objects[%d]\n%s' % (o.id, code)
    assert m.code == code
    assert m.func(1, 2) == (1, 2, re)


def test_dump_object():
    d = Database()
    parent_1 = d.create_object()
    parent_2 = d.create_object()
    assert d.dump_object(parent_1) == dict(
        id=parent_1.id, parents=[], properties=[], methods=[]
    )
    o = d.create_object()
    for parent in (parent_1, parent_2):
        o.add_parent(parent)
    actual = d.dump_object(o)
    expected = dict(
        id=o.id, properties=[], methods=[], parents=[parent_1.id, parent_2.id]
    )
    assert actual == expected


def test_load_object():
    d = Database()
    id = 18
    parent_1 = d.create_object()
    parent_2 = d.create_object()
    p = Property('property', 'Test property.', bool, False)
    m = Method(
        d, 'method', 'Test method.', 'a, b', ['import re'],
        'return (a, b, re)'
    )
    data = dict(
        id=id, methods=[d.dump_method(m)], properties=[d.dump_property(p)],
        parents=[]
    )
    o = d.load_object(data)
    assert d.objects[id] is o
    assert d.max_id == (id + 1)
    assert len(o._methods) == 1
    m.code = 'self = objects[%d]\n%s' % (id, m.code)
    m.func = None
    o._methods[m.name].func = None  # Otherwise they'll never match.
    assert o._methods[m.name] == m
    assert len(o._properties) == 1
    assert o._properties[p.name] == p
    assert not o._parents
    assert not o._children
    d.destroy_object(o)
    data['parents'].extend([parent_1.id, parent_2.id])
    o = d.load_object(data)
    assert o._parents == [parent_1, parent_2]
    assert parent_1._children == [o]
    assert parent_2._children == [o]


def test_maybe_load_object():
    d = Database()
    id = 1
    data = dict(properties=[], methods=[], parents=[], id=id)
    d.maybe_load_object(data)
    assert id in d.objects
    o = d.objects[id]
    assert len(d.objects) == 1
    data['parents'].append(id)
    id += 1
    data['id'] = id
    d.maybe_load_object(data)
    assert len(d.objects) == 2
    assert d.objects[id]._parents == [o]
    data['parents'].append(1234)
    with raises(CantLoadYetError):
        d.maybe_load_object(data)


def test_dump():
    d = Database()
    o1 = d.create_object()
    o2 = d.create_object()
    data = d.dump()
    assert len(data['objects']) == 2
    assert data['objects'][0]['id'] == o1.id
    assert data['objects'][1]['id'] == o2.id
