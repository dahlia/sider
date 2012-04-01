""":mod:`sider.entity.map` --- Mapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from ..types import Hash, ByteString
from .schema import Schema
from .exceptions import FieldError


class Map(Hash):
    """Maps a :class:`~sider.entity.schema.Schema` to a class.

    :param schema: the schema to map to the ``cls``
    :type schema: :class:`~sider.entity.schema.Schema`
    :param cls: the class to map to the ``schema``
    :type cls: :class:`type`

    """

    #: (:class:`sider.entity.schema.Schema`) The schema mapped to the
    #: :attr:`cls` (class).
    schema = None

    #: (:class:`type`) The class mapped to the :attr:`schema`.
    cls = None

    def __init__(self, schema, cls):
        if not isinstance(schema, Schema):
            raise TypeError('schema must be a sider.entity.schema.Schema, not '
                            + repr(schema))
        elif not isinstance(cls, type):
            raise TypeError('cls must be a class object, not ' + repr(cls))
        super(Map, self).__init__(key_type=ByteString, value_type=ByteString)
        self.schema = schema
        self.cls = cls

    def load_value(self, session, key):
        hash_ = super(Map, self).load_value(session, key)
        instance = object.__new__(self.cls)
        for name, field in self.schema.fields.iteritems():
            field_value = field.value_type.decode(hash_[name])
            object.__setattr__(instance, name, field_value)
        return instance

    def save_value(self, session, key, value):
        hash_ = {}
        for name, field in self.schema.fields.iteritems():
            try:
                field_value = object.__getattribute__(value, name)
            except AttributeError:
                field_value = None
            if field_value is None:
                if field.default is None and field.required:
                    raise FieldError('{0} field is required but missing in '
                                     '{1!r}'.format(name, value))
                field_value = field.default()
            hash_[name] = field.value_type.encode(field_value)
        super(Map, self).save_value(session, key, hash_)
        return value

