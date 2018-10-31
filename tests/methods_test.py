"""Test the Method class."""

import re
from types import FunctionType
from carehome import Method, Database

db = Database()
inserted_global = object()


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


def test_method_globals():
    db = Database(method_globals=dict(g=inserted_global))
    o = db.create_object()
    o.add_method('get_g', 'return g')
    assert o.get_g() is inserted_global
