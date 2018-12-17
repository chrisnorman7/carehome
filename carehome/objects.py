"""Provides the Object class."""

from types import MethodType
from attr import attrs, attrib, Factory
from .exc import DuplicateParentError, ParentIsChildError, NoSuchEventError

NoneType = type(None)


@attrs
class Object:
    """An object with multiple parents and multiple children."""

    database = attrib()
    _parents = attrib(default=Factory(list))
    _children = attrib(default=Factory(list))
    _methods = attrib(default=Factory(dict))
    _properties = attrib(default=Factory(dict))
    id = attrib(default=Factory(type(None)))
    _method_cache = attrib(default=Factory(dict), init=False, repr=False)
    _location = attrib(default=Factory(NoneType))

    def __attrs_post_init__(self):
        self.__initialised__ = True

    def __setattr__(self, name, value):
        initialised = '__initialised__' in self.__dict__
        reserved_names = ('__initialised__', 'id')
        if initialised and name in reserved_names:
                raise RuntimeError(
                    'You cannot set this attribute after initialisation.'
                )
        if not initialised or (
            name in self.__dict__ or name in dir(self.database.object_class)
        ):
            return super().__setattr__(name, value)
        elif name in self._properties:
            self._properties[name].set(value)
        else:
            prop = self.find_property(name)
            if prop is None:
                t = type(value)
                description = 'Added by __setattr__.'
            else:
                t = prop.type
                description = prop.description
            self.add_property(name, t, value, description=description)

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

    def descendants(self):
        """Return all descendants of this object."""
        for child in self._children:
            yield child
            for descendant in child.descendants():
                yield descendant

    def ancestors(self):
        """Return all the ancestors of this object."""
        for parent in self._parents:
            yield parent
            for ancestor in parent.ancestors():
                yield ancestor

    @property
    def location(self):
        if self._location is not None:
            return self.database.objects[self._location]

    @location.setter
    def location(self, obj):
        """Set the location of this object to a destination where. Note that
        where must either be an Object instance, or None, which means
        nowhere."""
        if self._location is not None:
            self.location.try_event('on_exit', self.location, self)
        if obj is None:
            value = None
        else:
            obj.try_event('on_enter', obj, self)
            value = obj.id
        self.__dict__['_location'] = value

    @property
    def contents(self):
        objects = self.database.objects.values()
        return [x for x in objects if x.location is self]

    def add_parent(self, obj):
        """Add a parent to this object."""
        assert isinstance(obj, type(self))
        if obj in self.descendants():
            raise ParentIsChildError(self, obj)
        if obj in self.ancestors() or obj is self:
            raise DuplicateParentError(self, obj)
        self.try_event('on_add_parent', self, obj)
        obj.try_event('on_add_child', obj, self)
        self._parents.append(obj)
        obj._children.append(self)

    def remove_parent(self, obj):
        """Remove a parent from this object."""
        self.try_event('on_remove_parent', self, obj)
        obj.try_event('on_remove_child', obj, self)
        self._parents.remove(obj)
        obj._children.remove(self)

    def method_or_property(self, attribute):
        """Get a method or property with the given name."""
        d = {}
        for dictionary in (self._properties, self._methods):
            d.update(dictionary)
        for name, value in d.items():
            if name == attribute:
                return value
        raise AttributeError(attribute)

    def __getattr__(self, name, *args, **kwargs):
        """Find a property or method matching the given name."""
        try:
            value = self.method_or_property(name)
        except AttributeError:
            for ancestor in self.ancestors():
                try:
                    value = ancestor.method_or_property(name)
                    break
                except AttributeError:
                    pass
            else:
                return super().__getattribute__(name, *args, **kwargs)
        if isinstance(value, self.database.property_class):
            return value.get()
        elif isinstance(value, self.database.method_class):
            num = id(value.func)
            if num not in self._method_cache:
                self._method_cache[num] = MethodType(value.func, self)
            return self._method_cache[num]
        else:
            return value

    def add_property(self, name, type, value, description=None):
        """Add a property to this Object."""
        if name in self._properties:
            raise NameError('Duplicate property name: %r.' % name)
        for cls in self.database.property_types.values():
            if cls is type:
                break
        else:
            raise TypeError(
                'Invalid property type for %r.%s (value=%r): %r.' % (
                    self, name, value, type
                )
            )
        if not isinstance(value, (NoneType, type)):
            raise TypeError('Value %r is not of type %r.' % (value, type))
        p = self.database.property_class(name, description, type, value)
        self.try_event('on_add_property', self, p)
        self._properties[name] = p
        return p

    def remove_property(self, name):
        """Remove a property from this object."""
        self.try_event('on_remove_property', self, name)
        del self._properties[name]

    def find_property(self, name):
        """Fnd a property with the given name and return it."""
        objects = [self]
        objects.extend(self.ancestors())
        for obj in objects:
            if name in obj.properties:
                return obj._properties[name]

    def add_method(self, *args, **kwargs):
        """Add a method to this object. All arguments are passed to the Method
        constructor. The first method argument must be self or similar, so this
        object can be available from within the function itself. Methods can
        not be added to anonymous objects (those with no IDs)."""
        if self.id is None:
            raise RuntimeError('Methods cannot be added to anonymous objects.')
        m = self.database.method_class(self.database, *args, **kwargs)
        self._methods[m.name] = m
        return m

    def remove_method(self, name):
        """Remove a method from this object."""
        del self._methods[name]

    def do_event(self, name, *args, **kwargs):
        """Call the named event with the given args and kwargs."""
        if callable(getattr(self, name, None)):
            return getattr(self, name)(*args, **kwargs)
        raise NoSuchEventError(self, name, args, kwargs)

    def try_event(self, name, *args, **kwargs):
        """Tries to run the given event. The return value is either None if the
        event is not present, or the return value of the vent method."""
        try:
            return self.do_event(name, *args, **kwargs)
        except NoSuchEventError:
            pass
