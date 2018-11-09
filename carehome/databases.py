"""Provides the Database class."""

import os
import os.path
from attr import attrs, attrib, Factory, asdict
from .objects import Object
from .property_types import property_types


@attrs
class ObjectReference:
    """A reference to an object. used when dumping and loading properties."""

    id = attrib()


@attrs
class Database:
    """A database which holds references to objects, methods to create and
    destroy them, and the current max ID."""

    objects = attrib(default=Factory(dict), init=False, repr=False)
    max_id = attrib(default=Factory(int), init=False)
    registered_objects = attrib(default=Factory(dict), init=False, repr=False)
    object_class = attrib(default=Factory(lambda: Object))
    property_types = attrib(default=Factory(lambda: property_types.copy()))
    method_globals = attrib(default=Factory(type(None)))
    methods_dir = attrib(default=Factory(lambda: 'methods'))

    def __attrs_post_init__(self):
        if not os.path.isdir(self.methods_dir):
            os.makedirs(self.methods_dir)
        if self.method_globals is None:
            self.method_globals = dict(database=self)
        self.method_globals.setdefault('objects', self.objects)
        self.property_types['obj'] = self.object_class

    def new_id(self):
        """Get a unique ID and increment self.max_id."""
        self.max_id += 1
        return self.max_id - 1

    def create_object(self, *parents):
        """Create an object that will be added to the dictionary of objects.
        This object will have all the provided parents added to it."""
        o = self.object_class(self, id=self.new_id())
        self.attach_object(o)
        for parent in parents:
            o.add_parent(parent)
        o.try_event('on_init')
        return o

    def attach_object(self, o):
        """Attach an Object instance o to this database."""
        self.max_id = max(o.id + 1, self.max_id)
        self.objects[o.id] = o

    def destroy_object(self, obj):
        """Destroy an object obj."""
        obj.try_event('on_destroy')
        for parent in obj._parents:
            obj.remove_parent(parent)
        del self.objects[obj.id]
        for name, value in self.registered_objects.items():
            if value is obj:
                del self.registered_objects[name]
                break

    def dump_value(self, value):
        """Return a properly dumped value. Used for converting Object instances
        to ObjectReference instances."""
        if isinstance(value, self.object_class):
            return ObjectReference(value.id)
        elif isinstance(value, list):
            return [self.dump_value(entry) for entry in value]
        elif isinstance(value, dict):
            return {
                self.dump_value(x): self.dump_value(y) for x, y in
                value.items()
            }
        else:
            return value

    def dump_property(self, p):
        """Return Property p as a dictionary."""
        pt = {y: x for x, y in self.property_types.items()}
        d = dict(
            type=pt.get(p.type, None), name=p.name, description=p.description,
            value=self.dump_value(p.value)
        )
        if d['type'] is None:
            raise RuntimeError('Invalid type on property %r.' % p)
        return d

    def load_value(self, value):
        """Returns a loaded value."""
        if isinstance(value, ObjectReference):
            return self.objects[value.id]
        elif isinstance(value, list):
            return [self.load_value(entry) for entry in value]
        elif isinstance(value, dict):
            return {
                self.load_value(x): self.load_value(y) for x, y
                in value.items()
            }
        else:
            return value

    def load_property(self, obj, d):
        """Load and return a Property instance bound to an Object instance obj,
        from a dictionary d."""
        return obj.add_property(
            d['name'], self.property_types.get(d['type']),
            self.load_value(d.get('value', None)),
            description=d.get('description', None)
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
        return obj.add_method(d['code'], d.get('name', None))

    def dump_object(self, obj):
        """Return Object obj as a dictionary."""
        return dict(
            id=obj.id, parents=[parent.id for parent in obj.parents],
            location=obj._location, properties=[
                self.dump_property(p) for p in obj._properties.values()
            ],
            methods=[self.dump_method(m) for m in obj._methods.values()]
        )

    def load_object(self, d):
        """Load and return an Object instance from a dictionary d."""
        o = self.object_class(self, id=d.get('id', self.max_id))
        o._location = d.get('location', None)
        self.attach_object(o)
        for data in d.get('methods', []):
            self.load_method(o, data)
        return o

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
        for data in objects:
            self.load_object(data)
        # All objects are now partially loaded without properties or parents.
        # Let's load the rest.
        for data in objects:
            obj = self.objects[data['id']]
            for datum in data['properties']:
                self.load_property(obj, datum)
            for id in data['parents']:
                obj.add_parent(self.objects[id])
        for name, id in d['registered_objects'].items():
            self.register_object(name, self.objects[id])

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

    def clear_method_cache(self):
        """Iterate through all objects and clear their method caches. This can
        conserve space, and should probably be run periodically on systems
        where methods change frequently."""
        for obj in self.objects.values():
            obj._method_cache.clear()

    def __getattr__(self, name):
        try:
            return self.registered_objects[name]
        except KeyError:
            return super().__getattribute__(name)
