"""Provides the Database class."""

from attr import attrs, attrib, Factory, asdict
from .objects import Object
from .property_types import PropertyTypes
from .exc import CantLoadYetError

property_types = {member.value: member.name for member in PropertyTypes}


@attrs
class Database:
    """A database which holds references to objects, methods to create and
    destroy them, and the current max ID."""

    objects = attrib(default=Factory(dict), init=False, repr=False)
    max_id = attrib(default=Factory(int), init=False)
    registered_objects = attrib(default=Factory(dict), init=False, repr=False)

    def create_object(self):
        """Create an object that will be added to the dictionary of objects."""
        o = Object(self, id=self.max_id)
        self.attach_object(o)
        return o

    def attach_object(self, o):
        """Attach an Object instance o to this database."""
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
        self.attach_object(o)
        for p in d['properties']:
            self.load_property(o, p)
        for m in d['methods']:
            self.load_method(o, m)
        for parent in d['parents']:
            o.add_parent(self.objects[parent])
        self.max_id = max(o.id + 1, self.max_id)
        return o

    def maybe_load_object(self, d):
        """Try and load an Object instance from a dictionary d, but raise
        CantLoadYetError if its parents haven't yet been loaded."""
        for parent in d['parents']:
            if parent not in self.objects:
                raise CantLoadYetError
        self.load_object(d)

    def dump(self):
        """Generate a dictionary from this database which can be dumped using
        YAML for example."""
        d = dict(objects=[], registered_objects={})
        for name, obj in self.registered_objects.items():
            d['registered_objects'][name] = obj.id
        for obj in sorted(self.objects.values(), key=lambda thing: thing.id):
            d['objects'].append(self.dump_object(obj))
        return d

    def load(self, d):
        """Load objects from a dictionary d."""
        objects = d['objects']
        while objects:
            datum = objects.pop(0)
            try:
                self.maybe_load_object(datum)
            except CantLoadYetError:
                objects.append(datum)  # Get it at the end.
        for name, id in d['registered_objects'].items():
            self.register_objects(name, self.objects[id])

    def register_object(self, name, obj):
        """Register an Object instance obj with this database. Once registered,
        it will be available as an attribute."""
        if obj.id is None:
            raise RuntimeError(
                'Cannot register an anonymous object: %r.' % obj
            )
        self.registered_objects[name] = obj

    def unregister_object(self, name):
        """Unregister an Object instance which was previously registered with
        the given name, so it is no longer available as an attribute."""
        del self.registered_objects[name]

    def __getattr__(self, name):
        try:
            return self.registered_objects[name]
        except KeyError:
            return super().__getattr__(name)
