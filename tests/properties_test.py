"""Test Property objects."""

from datetime import datetime
from pytest import raises
from carehome import Property


def test_init():
    description = 'Test property.'
    value = datetime.utcnow()
    p = Property(description, datetime, value)
    assert p.description == description
    assert p.type is datetime
    assert p.value == value


def test_get():
    value = 'Test'
    p = Property('Test property.', str, value)
    assert p.get() is value
    value = 'Some other value.'
    p.value = value
    assert p.get() is value


def test_set():
    value = 'Test value'
    p = Property('Test property.', str, value)
    with raises(TypeError):
        p.set(datetime.utcnow())
    assert p.value is value
    value = 'Some other value.'
    p.set(value)
    assert p.value is value
