"""Provides the Object class."""

from attr import attrs, attrib, Factory
from .exc import DuplicateParentError, ParentIsChildError
from .properties import Property
from .methods import Method


@attrs
class Object:
    """An object with multiple parents and multiple children."""

    database = attrib()
    _parents = attrib(default=Factory(list))
    _children = attrib(default=Factory(list))
    _methods = attrib(default=Factory(dict))
    _properties = attrib(default=Factory(dict))
    id = attrib(default=Factory(type(None)))

    def __attrs_post_init__(self):
        self.__initialised__ = True

    def __setattr__(self, name, value):
        if '__initialised__' not in self.__dict__:
            return super().__setattr__(name, value)
        if name in ('__initialised__', 'id'):
            raise RuntimeError(
                'You cannot set this attribute after initialisation.'
            )
        for property_name, property in self._properties.items():
            if property_name == name:
                property.set(value)
                break
        else:
            self.add_property(
                name, type(value), value, description='Added by __setattr__.'
            )

    @property
    def parents(self):
        return self._parents.copy()

    @property
    def children(self):
        return self._children.copy()

    @property
    def methods(self):
        return self._methods.keys()

    @property
    def properties(self):
        return self._properties.keys()

    @property
    def descendants(self):
        """Return all descendants of this object."""
        for child in self._children:
            yield child
            for descendant in child.descendants:
                yield descendant

    @property
    def ancestors(self):
        """Return all the ancestors of this object."""
        for parent in self._parents:
            yield parent
            for ancestor in parent.ancestors:
                yield ancestor

    def add_parent(self, obj):
        """Add a parent to this object."""
        assert isinstance(obj, type(self))
        if obj in self.descendants:
            raise ParentIsChildError(self, obj)
        if obj in self.ancestors:
            raise DuplicateParentError(self, obj)
        self._parents.append(obj)
        obj._children.append(self)

    def remove_parent(self, obj):
        """Remove a parent from this object."""
        self._parents.remove(obj)
        obj._children.remove(self)

    def method_or_property(self, attribute):
        """Get a method or property with the given name."""
        d = {}
        for dictionary in (self._properties, self._methods):
            d.update(dictionary)
        for name, value in d.items():
            if name == attribute:
                if isinstance(value, Property):
                    return value.get()
                elif isinstance(value, Method):
                    return value.func
                else:
                    return value
        raise AttributeError(attribute)

    def __getattr__(self, name, *args, **kwargs):
        """Find a property or method matching the given name."""
        try:
            return self.method_or_property(name)
        except AttributeError:
            for parent in self._parents:
                try:
                    return getattr(parent, name)
                except AttributeError:
                    pass
            return super().__getattribute__(name, *args, **kwargs)

    def add_property(self, name, type, value, description=None):
        """Add a property to this Object."""
        if name in self._properties:
            raise NameError('Duplicate property name: %r.' % name)
        for item in PropertyTypes:
            if item.value is type:
                break
        else:
            raise TypeError('Invalid property type: %r.' % type)
        if not isinstance(value, type):
            raise TypeError('Value %r is not of type %r.' % (value, type))
        p = Property(name, description, type, value)
        self._properties[name] = p
        return p

    def remove_property(self, name):
        """Remove a property from this object."""
        del self._properties[name]

    def add_method(self, name, code, args='', imports=(), description=None):
        """Add a method to this object. Args should be given as Python code,
        and imports should be a list of import statements. Both will be
        prepended to the function code. This object will be available in the
        function body as self. Methods can not be added to anonymous
        objects (those with no IDs)."""
        if self.id is None:
            raise RuntimeError('Methods cannot be added to anonymous objects.')
        code = 'self = objects[%d]\n%s' % (self.id, code)
        m = Method(
            self.database, name, description, args, imports, code
        )
        self._methods[name] = m
        return m

    def remove_method(self, name):
        """Remove a method from this object."""
        del self._methods[name]


from .property_types import PropertyTypes  # noqa: E402