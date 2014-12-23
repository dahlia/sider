import sys


if sys.version_info >= (3, 0, 0):
    basestring = str


class lower_sprintf_str(str):
    def __mod__(self, values):
        if not isinstance(values, tuple):
            values = values,
        values = tuple(s.lower() if isinstance(s, basestring) else s
                       for s in values)
        return str.__mod__(self, values)

