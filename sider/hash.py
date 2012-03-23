""":mod:`sider.hash` --- Hash objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import collections
from .session import Session
from .types import Bulk, ByteString


class Hash(collections.Mapping):
    """The Python-side representaion of Redis hash value.  It behaves
    such as built-in Python :class:`dict` object.  More exactly, it
    implements :class:`collections.Mapping` protocol.

    """

    #: (:class:`sider.types.Bulk`) The type of hash keys.
    key_type = None

    #: (:class:`sider.types.Bulk`) The type of hash values.
    value_type = None

    def __init__(self, session, key,
                 key_type=ByteString, value_type=ByteString):
        if not isinstance(session, Session):
            raise TypeError('session must be a sider.session.Session '
                            'instance, not ' + repr(session))
        self.session = session
        self.key = key
        self.key_type = Bulk.ensure_value_type(key_type, parameter='key_type')
        self.value_type = Bulk.ensure_value_type(value_type,
                                                 parameter='value_type')

    def __iter__(self):
        """Iterates over its :meth:`keys()`.

        :returns: the iterator which yields its keys
        :rtype: :class:`collections.Iterator`

        .. note::

           It is directly mapped to Redis :redis:`HKEYS` command.

        """
        keys = self.session.client.hkeys(self.key)
        decode = self.key_type.decode
        for key in keys:
            yield decode(key)

    def __len__(self):
        """Gets the number of items.

        :returns: the number of items
        :rtype: :class:`numbers.Integral`

        .. note::

           It is directly mapped to Redis :redis:`HLEN` command.

        """
        return self.session.client.hlen(self.key)

    def __contains__(self, key):
        """Tests whether the given ``key`` exists.

        :param key: the key
        :returns: ``True`` if the ``key`` exists or ``False``
        :rtype: :class:`bool`

        .. note::

           It is directly mapped to Redis :redis:`HEXISTS` command.

        """
        try:
            encoded_key = self.key_type.encode(key)
        except TypeError:
            return False
        exists = self.session.client.hexists(self.key, encoded_key)
        return bool(exists)

    def __getitem__(self, key):
        """Gets the value of the given ``key``.

        :param key: the key to get its value
        :returns: the value of the ``key``
        :raises: :exc:`TypeError` if the given ``key`` is not acceptable
                 by its :attr:`key_type`
        :raises: :exc:`KeyError` if there's no such ``key``

        .. note::

           It is directly mapped to Redis :redis:`HGET` command.

        """
        field = self.key_type.encode(key)
        value = self.session.client.hget(self.key, field)
        if value is None:
            raise KeyError(key)
        return self.value_type.decode(value)

    def _raw_update(self, value, pipe, encoded=False):
        items = getattr(value, 'iteritems', value.items)()
        if encoded:
            flatten = (val for k, v in items for val in (k, v))
        else:
            encode_key = self.key_type.encode
            encode_value = self.value_type.encode
            flatten = (val for k, v in items
                           for val in (encode_key(k), encode_value(v)))
        pipe.execute_command('HMSET', self.key, *flatten)

