"""Test the Method class."""

import re
from types import FunctionType
from carehome import Method, Database

db = Database()
inserted_global = object()


def test_init():
    name = 'test'
    description = 'This is a test.'
    m = Method(
        db, 'def %s(self):\n    """%s"""\n    print("Hello world.")' % (
            name, description
        )
    )
    assert isinstance(m.func, FunctionType)
    assert m.name == name
    f = m.func
    assert f.__name__ == name
    assert f.__doc__ == description


def test_run():
    m = Method(
        db, 'def test():\n    """Test function."""\n    return 12345'
    )
    assert m.func() == 12345


def test_args():
    m = Method(
        db, 'def test(a, b=5):\n    """Test function."""\n    return (a, b)'
    )
    assert m.func(1) == (1, 5)
    assert m.func(4, b=10) == (4, 10)


def test_imports():
    m = Method(db, 'import re\ndef test():\n    """Test re."""\n    return re')
    assert m.func() is re


def test_method_globals():
    db = Database(method_globals=dict(g=inserted_global))
    o = db.create_object()
    o.add_method('def get_g(self):\n    return g')
    assert o.get_g() is inserted_global
