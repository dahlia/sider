""":mod:`sider.entity.map` --- Mapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from ..types import Hash, ByteString
from .schema import Schema
from .exceptions import KeyFieldError, FieldError


class Map(Hash):
    """Maps a :class:`~sider.entity.schema.Schema` to a class.

    :param schema: the schema to map to the ``cls``
    :type schema: :class:`~sider.entity.schema.Schema`
    :param cls: the class to map to the ``schema``
    :type cls: :class:`type`

    .. todo::

       Currently it unconditionally creates every instance even if it
       already exists in :class:`~sider.session.Session.identity_map`
       when it's loaded (:meth:`load_value()`).

       We can skip this unnecessary inefficient work.

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
        entity_key = None
        for name, field in self.schema.fields.iteritems():
            field_value = field.value_type.decode(hash_[field.name])
            object.__setattr__(instance, name, field_value)
            if field.key:
                entity_key = field_value
        assert entity_key is not None
        idmap = session.identity_map.setdefault(self, {})
        try:
            return idmap[entity_key]
        except KeyError:
            pass
        idmap[entity_key] = instance
        return instance

    def save_value(self, session, key, value):
        if not isinstance(value, self.cls):
            msg = 'expected an instance of {0}.{1}, not {2!r}'.format(
                self.cls.__module__, self.cls.__name__, value
            )
            raise TypeError(msg)
        hash_ = {}
        entity_key = self.schema.get_key(value)
        identity_map = session.identity_map.setdefault(self, {})
        try:
            already_exists = identity_map[entity_key]
        except KeyError:
            pass
        else:
            if already_exists is not value:
                raise KeyFieldError(
                    'there is already an entity of the same key: ' +
                    repr(already_exists)
                )
        for name, field in self.schema.fields.iteritems():
            try:
                field_value = object.__getattribute__(value, name)
            except AttributeError:
                field_value = None
            if field_value is None:
                if field.default is not None:
                    field_value = field.default()
                    object.__setattr__(value, name, field_value)
                elif field.required:
                    raise FieldError('{0} field is required but missing in '
                                     '{1!r}'.format(name, value))
            if field_value is not None:
                hash_[field.name] = field.value_type.encode(field_value)
        super(Map, self).save_value(session, key, hash_)
        identity_map[entity_key] = value
        return value

    def __hash__(self):
        return id(self)

    def __eq__(self, operand):
        return self is operand

