""":mod:`sider.entity.schema` --- Schema
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import collections
from ..types import Bulk
from .exceptions import KeyFieldError


class Field(object):
    """The spec of a field.

    :param value_type: the type of the field value
    :type value_type: :class:`sider.types.Bulk`, :class:`type`
    :param required: whether the field is required or optional.
                     ``True`` if it's required or ``False`` if it's
                     optional.  default vary depending ``key`` option
    :type required: :class:`bool`
    :param unique: whether the field value has to be unique for
                   the entity.  ``True`` if it has to be unique.
                   default very depending ``key`` option
    :type unique: :class:`bool`
    :param key: whether it's the key field of the entity.
                if it's ``True``, ``required`` and ``unique`` both
                must be ``True`` (it will be automatically turned on
                if you simply omit to specify these options.)
                default is ``False``
    :param default: the default value, or a function that returns it
                    of the field.  by default default value is just
                    ``None``.  if it's callable, the default value
                    will be made by it.  or if it's not callable,
                    it will just become the default value except
                    ``None``.  ``None`` means "no default".
                    to disambiguate it you can pass a function that
                    simply returns the value e.g. ``lambda: value``
                    or use :class:`ConstantFunction`
    :param name: the actual key name of Redis hash.  it would be
                 automatically determined by :class:`Schema`
                 according to its keyword name if it is kept
                 to ``None``.  the default is ``None``
    :type name: :class:`str`

    """

    #: (:class:`str`) The actual key name of Redis hash.  It would be
    #: automatically determined by :class:`Schema` according to its
    #: keyword name if it is kept to ``None``.
    name = None

    #: (:class:`sider.types.Bulk`) The type of the field value.
    value_type = None

    #: (:class:`bool`) ``True`` if the field is required or ``False``
    #: if it's optional
    required = None

    #: (:class:`bool`) ``True`` if the field has to be unique for
    #: the entity or ``False``.
    unique = None

    #: (:class:`bool`) Whether it's the key field of the entity.
    #: Guarentees :attr:`required` and :attr:`unique` both are ``True``
    #: if :attr:`key` is ``True``
    key = None

    #: (:class:`collections.Callable`) The nullary function that takes
    #: no arguments and simply returns a default value.  It can be
    #: ``None`` if there's no function that returns default value.
    default = None

    def __init__(self, value_type, required=None, unique=None, key=False,
                 default=None, name=None):
        self.value_type = Bulk.ensure_value_type(value_type,
                                                 parameter='value_type')
        if not (name is None or isinstance(name, basestring)):
            raise TypeError('name must be a string, not ' + repr(name))
        if default is not None and not callable(default):
            default = ConstantFunction(default)
        if key:
            if required is None:
                required = True
            if unique is None:
                unique = True
            if not required:
                raise TypeError('the key field cannot be optional')
            elif not unique:
                raise TypeError('the key field must be unique')
        self.name = str(name) if name else None
        self.required = required
        self.unique = unique
        self.key = bool(key)
        self.default = default


class Schema(object):
    """The schema of an entity.

    :param \*\*fields: the :class:`Field` objects for these names.
                       there must be one key field
    :raises sider.entity.exceptions.KeyFieldError:
        when there's no key field or two or more key fields

    """

    #: (:class:`collections.Mapping`) The map of fields.
    #: Keys are mapped attribute names.
    fields = None

    #: (:class:`collections.Mapping`) The map of fields.
    #: Keys are Redis hash key names.
    names = None

    #: (:class:`Field`) The key field.
    key_field = None

    #: (:class:`str`) The name of the key field.
    key_field_name = None

    def __init__(self, **fields):
        self.fields = fields
        names = {}
        key_fields = {}
        for name, field in fields.iteritems():
            if field.key:
                key_fields[name] = field
                self.key_field_name = name
                self.key_field = field
            if not field.name:
                field.name = name
            names[field.name] = field
        self.names = names
        if not key_fields:
            raise KeyFieldError('the key field is missing; there must be '
                                'a key field for every schema')
        elif len(key_fields) > 1:
            key_len = len(key_fields)
            keys = ', '.join(repr(name)
                             for name, field in key_fields.iteritems())
            raise KeyFieldError('the key field must be one, but {0} fields '
                                'were marked as key: {1}'.format(key_len, keys))


class ConstantFunction(collections.Callable):
    """The simple function object that returns a specific :attr:`value`.
    This object is :class:`~collections.Callable`.

    :param value: the value this function would return

    .. note::

       It is internally used for :attr:`Field.default`.

    """

    #: The value this function would return
    value = None

    def __init__(self, value):
        self.value = value

    def __call__(self):
        return self.value

