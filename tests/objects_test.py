"""Test objects."""

from pytest import raises
from carehome import objects
from carehome.exc import DuplicateParentError, ParentIsChildError

Object = objects.Object


def test_max_id():
    assert objects.max_id == 0


def test_creation():
    o = Object()
    assert o in objects.objects
    assert objects.max_id == 1
    assert o._properties == {}
    assert o._methods == {}
    assert o._parents == []
    assert o._children == []
    assert o.parents == []
    assert o.children == []


def test_properties():
    o = Object()
    o._properties['hello'] = 'world'
    assert o.hello == 'world'
    with raises(AttributeError):
        print(o.test)


def test_add_parent():
    parent = Object()
    child = Object()
    child.add_parent(parent)
    assert parent in child.parents
    with raises(DuplicateParentError):
        child.add_parent(parent)
    with raises(ParentIsChildError):
        parent.add_parent(child)


def test_properties_inheritance():
    parent = Object()
    child = Object()
    child.add_parent(parent)
    parent._properties['hello'] = 'world'
    assert child.hello == 'world'
    assert parent.hello == 'world'
    child._properties['hello'] = 'test'
    assert parent.hello == 'world'
    assert child.hello == 'test'
