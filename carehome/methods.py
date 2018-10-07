"""Provides the Method class."""

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
        g['database'] = self.database
        g['objects'] = self.database.objects
        code = '\n'.join(self.imports)
        code += '\ndef %s(%s):\n    """%s"""' % (
            self.name, self.args, self.description
        )
        for line in self.code.splitlines():
            code += '\n    '
            code += line
        source = compile(code, f'<Method {self.name}>', 'exec')
        eval(source, g)
        self.func = g[self.name]
