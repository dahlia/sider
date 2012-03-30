""":mod:`sider.entity.exceptions` --- Exceptions types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""


class FieldError(AttributeError):
    """A subtype of :exc:`~exceptions.AttributeError`.
    It will be raised when the error related an entity field happens.

    """


class KeyFieldError(FieldError):
    """A subtype of :exc:`FieldError`.  It will be raised when the
    error related a key field of entities happens.

    """

