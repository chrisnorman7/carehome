"""The carehome module. Allows you to build MOO-like object-oriented objects in
Python."""

from .objects import Object
from .properties import Property
from .property_types import property_types
from .methods import Method
from .databases import Database, ObjectReference

__all__ = ['property_types']

for thing in (
    Object, Property, Method, Database, ObjectReference
):
    __all__.append(thing.__name__)
