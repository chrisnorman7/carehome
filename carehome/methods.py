"""Provides the Method class."""

import os
import os.path
from attr import attrs, attrib, Factory


@attrs
class Method:
    """An Object method."""

    database = attrib()
    name = attrib()
    description = attrib()
    args = attrib()
    imports = attrib()
    code = attrib()
    func = attrib(default=Factory(type(None)), init=False)

    def __attrs_post_init__(self):
        g = globals().copy()
        g.update(**self.database.method_globals)
        g['objects'] = self.database.objects
        code = '\n'.join(self.imports)
        code += '\ndef %s(%s):\n    """%s"""' % (
            self.name, self.args, self.description
        )
        for line in self.code.splitlines():
            code += '\n    '
            code += line
        n = self.get_filename()
        with open(n, 'w') as f:
            f.write(code)
        source = compile(code, n, 'exec')
        eval(source, g)
        self.func = g[self.name]

    def get_filename(self):
        """Get a unique filename for this method."""
        return os.path.join(
            self.database.methods_dir, '%s-%d.method' % (self.name, id(self))
        )
