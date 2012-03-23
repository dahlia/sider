""":mod:`sider.hash` --- Hash objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import collections
from .session import Session
from .types import Bulk, ByteString


class Hash(collections.MutableMapping):
    """The Python-side representaion of Redis hash value.  It behaves
    such as built-in Python :class:`dict` object.  More exactly, it
    implements :class:`collections.MutableMapping` protocol.

    .. table:: Mappings of Redis commands--:class:`Hash` methods

       ===================== ===========================================
       Redis commands        :class:`Hash` methods
       ===================== ===========================================
       :redis:`DEL`          :meth:`Hash.clear()`
       :redis:`HDEL`         :keyword:`del` (:meth:`Hash.__delitem__()`)
       :redis:`HEXISTS`      :keyword:`in` (:meth:`Hash.__contains__()`)
       :redis:`HGET`         :meth:`Hash.__getitem__()`,
                             :meth:`Hash.get()`
       :redis:`HGETALL`      :meth:`Hash.items()`
       :redis:`HINCRBY`      N/A
       :redis:`HINCRBYFLOAT` N/A
       :redis:`HKEYS`        :func:`iter()` (:meth:`Hash.__iter__()`),
                             :meth:`Hash.keys()`
       :redis:`HLEN`         :func:`len()` (:meth:`Hash.__len__()`)
       :redis:`HMGET`        N/A
       :redis:`HMSET`        :meth:`Hash.update()`
       :redis:`HSET`         :token:`=` (:meth:`Hash.__setitem__()`)
       :redis:`HSETNX`       :meth:`Hash.setdefault()`
       :redis:`HVALS`        :meth:`Hash.values()`
       N/A                   :meth:`Hash.pop()`
       N/A                   :meth:`Hash.popitem()`
       ===================== ===========================================

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
        :raises: :exc:`~exceptions.TypeError` if the given ``key``
                 is not acceptable by its :attr:`key_type`
        :raises: :exc:`~exceptions.KeyError` if there's no
                 such ``key``

        .. note::

           It is directly mapped to Redis :redis:`HGET` command.

        """
        field = self.key_type.encode(key)
        value = self.session.client.hget(self.key, field)
        if value is None:
            raise KeyError(key)
        return self.value_type.decode(value)

    def __setitem__(self, key, value):
        """Sets the ``key`` with the ``value``.

        :param key: the key to set
        :param value: the value to set
        :raises: :exc:`~exceptions.TypeError` if the given ``key``
                 is not acceptable by its :attr:`key_type` or
                 the given ``value`` is not acceptable by
                 its :attr:`value_type`

        .. note::

           It is directly mapped to Redis :redis:`HSET` command.

        """
        encoded_key = self.key_type.encode(key)
        encoded_val = self.value_type.encode(value)
        self.session.client.hset(self.key, encoded_key, encoded_val)

    def __delitem__(self, key):
        """Removes the ``key``.

        :param key: the key to delete
        :raises: :exc:`~exceptions.TypeError` if the given ``key``
                 is not acceptable by its :attr:`key_type`
        :raises: :exc:`~exceptions.KeyError` if there's no
                 such ``key``

        .. note::

           It is directly mapped to Redis :redis:`HDEL` command.

        """
        encoded = self.key_type.encode(key)
        ok = self.session.client.hdel(self.key, encoded)
        if not ok:
            raise KeyError(key)

    def keys(self):
        """Gets its all keys.  Equivalent to :meth:`__iter__()` except
        it returns a :class:`~collections.Set` instead of iterable.
        There isn't any meaningful order of keys.

        :returns: the set of its all keys
        :rtype: :class:`collections.KeysView`

        .. note::

           This method is directly mapped to Redis :redis:`HKEYS`
           command.

        """
        return frozenset(self)

    def values(self):
        """Gets its all values.  It returns a :class:`list` but
        there isn't any meaningful order of values.

        :returns: its all values
        :rtype: :class:`collections.ValuesView`

        .. note::

           This method is directly mapped to Redis :redis:`HVALS`
           command.

        """
        values = self.session.client.hvals(self.key)
        decode = self.value_type.decode
        for i, val in enumerate(values):
            values[i] = decode(val)
        return values

    def items(self):
        """Gets its all ``(key, value)`` pairs.
        There isn't any meaningful order of pairs.

        :returns: the set of ``(key, value)`` pairs (:class:`tuple`)
        :rtype: :class:`collections.ItemsView`

        .. note::

           This method is mapped to Redis :redis:`HGETALL` command.

        """
        items = self.session.client.hgetall(self.key)
        decode_key = self.key_type.decode
        decode_value = self.value_type.decode
        return frozenset((decode_key(k), decode_value(v))
                         for k, v in items.iteritems())

    def clear(self):
        """Removes all items from this hash.

        .. note::

           Under the hood it simply :redis:`DEL` the key.

        """
        self.session.client.delete(self.key)

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


