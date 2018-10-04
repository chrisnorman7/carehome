"""Test the Method class."""

import re
from types import FunctionType
from carehome import Method


def test_init():
    m = Method('test', 'Test method.', '', [], 'print("Hello world.")')
    assert isinstance(m.func, FunctionType)
    assert m.name == 'test'
    f = m.func
    assert f.__name__ == 'test'
    assert f.__doc__ == m.description


def test_run():
    m = Method('test', 'Test function.', '', [], 'return 12345')
    assert m.func() == 12345


def test_args():
    m = Method('test', 'Test function.', 'a, b=5', [], 'return (a, b)')
    assert m.func(1) == (1, 5)
    assert m.func(4, b=10) == (4, 10)


def test_imports():
    m = Method('test', 'Test re.', '', ['import re'], 'return re')
    assert m.func() is re
