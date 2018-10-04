"""Test Database objects."""

import re
from datetime import datetime
from pytest import raises
from carehome import Database, Object, Property, Method


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
    name = 'test'
    desc = 'Test date.'
    value = datetime.utcnow()
    p = d.load_property(
        dict(name=name, type='datetime', value=value, description=desc)
    )
    assert p.value == value
    assert p.type is datetime
    assert p.description == desc


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
    name = 'test'
    description = 'This is a test function.'
    args = 'a, b'
    imports = ['import re']
    code = 'return (a, b, re)'
    m = d.load_method(
        dict(
            name=name, description=description, args=args, imports=imports,
            code=code
        )
    )
    assert m.database is d
    assert m.name == name
    assert m.description == description
    assert m.args == args
    assert m.imports == imports
    assert m.code == code
    assert m.func(1, 2) == (1, 2, re)
