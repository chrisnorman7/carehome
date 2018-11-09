"""Provides the Method class."""

import os
import os.path
from inspect import isfunction
from attr import attrs, attrib, Factory

NoneType = type(None)


@attrs
class Method:
    """An Object method."""

    database = attrib()
    code = attrib()
    name = attrib(default=Factory(NoneType))
    func = attrib(default=Factory(NoneType), init=False)

    def __attrs_post_init__(self):
        g = globals().copy()
        g.update(**self.database.method_globals)
        old_names = set(g.keys())
        n = self.get_filename()
        with open(n, 'w') as f:
            f.write(self.code)
        source = compile(self.code, n, 'exec')
        eval(source, g)
        if self.name is None:
            new_names = set(g.keys())
            for name in new_names.difference(old_names):
                f = g[name]
                if isfunction(f):
                    self.name = name
                    self.func = f
                    break
            else:
                raise RuntimeError('No function found.')
        else:
            self.func = g[self.name]

    def get_filename(self):
        """Get a unique filename for this method."""
        return os.path.join(
            self.database.methods_dir, '%s-%d.method' % (self.name, id(self))
        )
