"""The carehome module. Allows you to build MOO-like object-oriented objects in
Python."""

from .objects import Object
from .properties import Property
from .property_types import PropertyTypes
from .methods import Method
from .databases import Database, ObjectReference

__all__ = []

for thing in (
    Object, Property, Method, Database, PropertyTypes, ObjectReference
):
    __all__.append(thing.__name__)
