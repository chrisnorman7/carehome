"""Provides exception classes."""


class CarehomeError(Exception):
    """All other errors should inherit from this class."""


class InheritanceError(CarehomeError):
    """An error in the inheritance hierarchy."""


class DuplicateParentError(InheritanceError):
    """This object already has this parent."""


class DuplicateChildError(InheritanceError):
    """This object already has this child."""


class ParentIsChildError(InheritanceError):
    """This parent is already a child of this object."""


class DatabaseError(CarehomeError):
    """There is a problem in the database."""


class NoSuchEventError(CarehomeError):
    """No such event."""


class Flake8NotFound(CarehomeError):
    """Flake8 not found."""


class LoadError(CarehomeError):
    """Error loading something."""


class LoadPropertyError(LoadError):
    """Error loading a property."""


class LoadMethodError(LoadError):
    """Error loading a method."""


class LoadObjectError(LoadError):
    """Error loading an object."""


class DestroyError(CarehomeError):
    """Error destroying an object."""


class ObjectRegisteredError(DestroyError):
    """Object is registered."""


class HasChildrenError(DestroyError):
    """This object has children."""


class HasContentsError(DestroyError):
    """Object has contents."""


class IsValueError(DestroyError):
    """This object is stored in the property of another object."""
