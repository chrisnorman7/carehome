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


class CantLoadYetError(DatabaseError):
    """Can't load this object before its parents."""
