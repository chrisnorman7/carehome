"""Provides the Property class."""

from datetime import datetime
from enum import Enum
from attr import attrs, attrib
from . import Object


class PropertyTypes(Enum):
    """The available property types."""

    str = str
    float = float
    int = int
    list = list
    dict = dict
    datetime = datetime
    obj = Object


@attrs
class Property:
    """A property on an Object instance."""

    description = attrib()
    type = attrib()
    value = attrib()

    def get(self):
        return self.value

    def set(self, value):
        if not isinstance(value, self.type):
            raise TypeError(
                'Type mismatch for property %r. Value: %r.' % (self, value)
            )
        self.value = value
