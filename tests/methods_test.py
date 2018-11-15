"""Test the Method class."""

import os
import os.path
import re
from inspect import isclass, isfunction
from types import FunctionType
import flake8
from pytest import raises
from carehome import Method, Database, methods
from carehome.exc import Flake8NotFound

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


def test_get_filename():
    m = Method(db, 'def test_filename():\n    print()', name='test_filename')
    assert os.path.isfile(m.get_filename())
    with open(m.get_filename(), 'r') as f:
        assert f.read() == m.code


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


def test_no_func():
    with raises(RuntimeError):
        Method(db, 'import sys')


def test_flake8():
    assert methods.flake8 is flake8
    m = Method(db, 'def f():\n    pass\n')
    methods.flake8 = None
    with raises(Flake8NotFound):
        m.validate_code()
    methods.flake8 = flake8
    assert m.validate_code() is None
    m = Method(db, 'def f():\n    return something\n', name='f')
    with raises(NameError):
        m.func()
    expected = "stdin:2:12: F821 undefined name 'something'%s" % os.linesep
    res = m.validate_code()
    assert res == expected
    db.method_globals['pretend'] = 1234
    m = Method(db, 'def f():\n    return pretend\n', name='f')
    assert m.validate_code() is None
