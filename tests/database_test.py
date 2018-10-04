"""Test Database objects."""

from carehome import Database, Object


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
