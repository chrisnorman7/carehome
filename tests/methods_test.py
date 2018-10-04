"""Test the Method class."""

import re
from types import FunctionType
from carehome import Method, Database

db = Database()


def test_init():
    m = Method(db, 'test', 'Test method.', '', [], 'print("Hello world.")')
    assert isinstance(m.func, FunctionType)
    assert m.name == 'test'
    f = m.func
    assert f.__name__ == 'test'
    assert f.__doc__ == m.description


def test_run():
    m = Method(db, 'test', 'Test function.', '', [], 'return 12345')
    assert m.func() == 12345


def test_args():
    m = Method(db, 'test', 'Test function.', 'a, b=5', [], 'return (a, b)')
    assert m.func(1) == (1, 5)
    assert m.func(4, b=10) == (4, 10)


def test_imports():
    m = Method(db, 'test', 'Test re.', '', ['import re'], 'return re')
    assert m.func() is re
