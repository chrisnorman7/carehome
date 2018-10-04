"""Provides the Database class."""

from attr import attrs, attrib, Factory, asdict
from .objects import Object
from .property_types import PropertyTypes
from .properties import Property
from .methods import Method

property_types = {member.value: member.name for member in PropertyTypes}


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

    def dump_property(self, p):
        """Return Property p as a dictionary."""
        d = asdict(p)
        d['type'] = property_types.get(d['type'], None)
        if d['type'] is None:
            raise RuntimeError('Invalid type on property %r.' % p)
        return d

    def load_property(self, d):
        """Load and return a Property instance from a dictionary d."""
        return Property(
            d['name'], d['description'],
            getattr(PropertyTypes, d['type']).value, d['value']
        )

    def dump_method(self, m):
        """Dump a Method m as a dictionary."""
        return asdict(
            m, filter=lambda attribute, value: attribute.name not in (
                'database', 'func'
            )
        )

    def load_method(self, d):
        """Load and return a Method instance from a dictionary d."""
        return Method(
            self, d['name'], d['description'], d['args'], d['imports'],
            d['code']
        )

    def as_dict(self):
        """Generate a dictionary from this database which can be dumped using
        YAML for example."""
        d = dict(objects=[])
        for obj in sorted(self.objects, lambda thing: thing.id):
            parents = [parent.id for parent in obj.parents]
            o = dict(parents=parents, id=obj.id)
            properties = [
                self.dump_property(p) for p in obj._properties.values()
            ]
            o['properties'] = properties
            d['objects'].append(o)
        return d
