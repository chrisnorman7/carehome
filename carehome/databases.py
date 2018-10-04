"""Provides the Database class."""

from attr import attrs, attrib, Factory, asdict
from .objects import Object
from .property_types import PropertyTypes

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
        self.register_object(o)
        return o

    def register_object(self, o):
        """Register an Object instance o with this database."""
        self.max_id = max(o.id + 1, self.max_id)
        self.objects[o.id] = o

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

    def load_property(self, obj, d):
        """Load and return a Property instance bound to an Object instance obj,
        from a dictionary d."""
        return obj.add_property(
            d['name'], getattr(PropertyTypes, d['type']).value, d['value'],
            description=d['description']
        )

    def dump_method(self, m):
        """Dump a Method m as a dictionary."""
        return asdict(
            m, filter=lambda attribute, value: attribute.name not in (
                'database', 'func'
            )
        )

    def load_method(self, obj, d):
        """Load and return a Method instance bound to Object instance obj, from
        a dictionary d."""
        return obj.add_method(
            d['name'], d['code'], args=d['args'], imports=d['imports'],
            description=d['description']
        )

    def dump_object(self, obj):
        """Return Object obj as a dictionary."""
        return dict(
            id=obj.id, parents=[parent.id for parent in obj.parents],
            properties=[
                self.dump_property(p) for p in obj._properties.values()
            ],
            methods=[self.dump_method(m) for m in obj._methods.values()]
        )

    def load_object(self, d):
        """Load and return an Object instance from a dictionary d."""
        o = Object(self, id=d['id'])
        self.register_object(o)
        for p in d['properties']:
            self.load_property(o, p)
        for m in d['methods']:
            self.load_method(o, m)
        for parent in d['parents']:
            o.add_parent(self.objects[parent])
        self.max_id = max(o.id + 1, self.max_id)
        return o

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
