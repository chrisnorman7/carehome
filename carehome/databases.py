"""Provides the Database class."""

from attr import attrs, attrib, Factory
from .objects import Object


@attrs
class Database:
    """A database which holds references to objects, methods to create and
    destroy them, and the current max ID."""

    objects = attrib(default=Factory(dict), init=False, repr=False)
    max_id = attrib(default=Factory(int), init=False)

    def create_object(self):
        """Create an object that will be added to the dictionary of objects."""
        o = Object(self, id=self.max_id)
        self.max_id += 1
        self.objects[o.id] = o
        return o

    def destroy_object(self, obj):
        """Destroy an object obj."""
        for parent in obj._parents:
            parent.remove_parent(obj)
        del self.objects[obj.id]
