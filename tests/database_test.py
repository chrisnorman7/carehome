"""Test Database objects."""

from datetime import datetime
from pytest import raises
from carehome import Database, Object, Property


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
