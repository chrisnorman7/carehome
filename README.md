# Carehome
A stupidly named package for creating MOO-style objects with Python.

Objects support multiple inheritance, properties, events, and methods. The
resulting database can be dumped and loaded to and from dictionary objects.

## Events
The following events are used throughout the code. Any other events which are
baked into the main code base will be added here.

### on_init
Called when the object is initialised.

#### Arguments
* The object that is being initialised. This allows the event call to propagate
up the object hierarchy.

### on_attach
Called when the object is attached to the database.

#### Arguments
* The object that is being initialised. This allows the event call to propagate
up the object hierarchy.

### on_destroy
Called before the object is destroyed, and the object is still valid.

#### Arguments
* The object that is being initialised. This allows the event call to propagate
up the object hierarchy.

### on_enter
Called before an object enters another one.

#### Arguments
* The new location of this object.
* The thing which is moving into this object.

### on_exit
Called before an object exits another.

#### Arguments
* The old location of this object.
* The object which is leaving.

### on_add_parent
Called before a parent is added to this object.

#### Arguments
* The object that is being initialised. This allows the event call to propagate
up the object hierarchy.
* The parent which is being added.

### on_add_child
Called before this object gains a child.

#### Arguments
* The object that is being initialised. This allows the event call to propagate
up the object hierarchy.
* The child which is being added.

### on_remove_parent
Called before a parent is removed from this object.

#### Arguments
* The object that is being initialised. This allows the event call to propagate
up the object hierarchy.
* The parent which is being removed.

### on_remove_child
Called before a child is removed from this object.

#### Arguments
* The object that is being initialised. This allows the event call to propagate
up the object hierarchy.
* The child which is being removed.

### on_add_property
Called before a property is added to this object.

#### Arguments
* The object that is being initialised. This allows the event call to propagate
up the object hierarchy.
* The new Property instance.

### on_remove_property
Called before a property is removed from this object.

#### Arguments
* The object that is being initialised. This allows the event call to propagate
up the object hierarchy.
* The name of the old property.
