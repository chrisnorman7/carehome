"""Provides the Property class."""

from attr import attrs, attrib


@attrs
class Property:
    """A property on an Object instance."""

    name = attrib()
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
