"""Clear the methods directory before we start."""

from shutil import rmtree
from pytest import fixture


@fixture(scope='session', autouse=True)
def clear_method_files():
    """First we yield to start the tests."""
    yield  # Test, test, test!
    rmtree('methods')
