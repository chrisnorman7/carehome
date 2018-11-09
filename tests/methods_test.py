"""Test the Method class."""

import re
from inspect import isclass, isfunction
from types import FunctionType
from carehome import Method, Database

db = Database()
inserted_global = object()

code = """
class Thing:
    pass


def f1():
    return 1


def f2():
    return 2


def f():
    return (Thing, f1, f2)
"""


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


def test_created():
    m = Method(db, code, name='f')
    Thing, f1, f2 = m.func()
    # Make sure the right stuff has been returned.
    assert isclass(Thing)
    assert isfunction(f1)
    assert isfunction(f2)
    assert f1() == 1
    assert f2() == 2
    assert m.created['Thing'] is Thing
    assert m.created['f1'] is f1
    assert m.created['f2'] is f2


def test_method_guess_name():
    m = Method(db, 'def f():\n    return 1234')
    assert m.name == 'f'
    assert m.func() == 1234
