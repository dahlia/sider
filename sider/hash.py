""":mod:`sider.hash` --- Hash objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. seealso::

    `Redis Data Types <http://redis.io/topics/data-types>`_
       The Redis documentation that explains about its data
       types: strings, lists, sets, sorted sets and hashes.

"""
import collections
from .session import Session
from .types import Bulk, String
from .transaction import query, manipulative
from . import utils


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
                 key_type=String, value_type=String):
        if not isinstance(session, Session):
            raise TypeError('session must be a sider.session.Session '
                            'instance, not ' + repr(session))
        self.session = session
        self.key = key
        self.key_type = Bulk.ensure_value_type(key_type, parameter='key_type')
        self.value_type = Bulk.ensure_value_type(value_type,
                                                 parameter='value_type')

    @query
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

    @query
    def __len__(self):
        """Gets the number of items.

        :returns: the number of items
        :rtype: :class:`numbers.Integral`

        .. note::

           It is directly mapped to Redis :redis:`HLEN` command.

        """
        return self.session.client.hlen(self.key)

    @query
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

    @query
    def __getitem__(self, key):
        """Gets the value of the given ``key``.

        :param key: the key to get its value
        :returns: the value of the ``key``
        :raises exceptions.TypeError:
           if the given ``key`` is not acceptable by
           its :attr:`key_type`
        :raises exceptions.KeyError:
           if there's no such ``key``

        .. note::

           It is directly mapped to Redis :redis:`HGET` command.

        """
        field = self.key_type.encode(key)
        value = self.session.client.hget(self.key, field)
        if value is None:
            raise KeyError(key)
        return self.value_type.decode(value)

    @manipulative
    def __setitem__(self, key, value):
        """Sets the ``key`` with the ``value``.

        :param key: the key to set
        :param value: the value to set
        :raises exceptions.TypeError:
           if the given ``key`` is not acceptable by
           its :attr:`key_type` or the given ``value``
           is not acceptable by its :attr:`value_type`

        .. note::

           It is directly mapped to Redis :redis:`HSET` command.

        """
        encoded_key = self.key_type.encode(key)
        encoded_val = self.value_type.encode(value)
        self.session.client.hset(self.key, encoded_key, encoded_val)

    def __delitem__(self, key):
        """Removes the ``key``.

        :param key: the key to delete
        :raises exceptions.TypeError:
           if the given ``key`` is not acceptable by
           its :attr:`key_type`
        :raises exceptions.KeyError:
           if there's no such ``key``

        .. note::

           It is directly mapped to Redis :redis:`HDEL` command.

        """
        session = self.session
        encoded = self.key_type.encode(key)
        if session.current_transaction is None:
            ok = session.client.hdel(self.key, encoded)
        else:
            session.mark_query([self.key])
            ok = session.client.hexists(self.key, encoded)
            if ok:
                session.mark_manipulative()
                session.client.hdel(self.key, encoded)
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

    @query
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

    @query
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
        return frozenset((decode_key(k), decode_value(items[k]))
                         for k in items)

    @manipulative
    def clear(self):
        """Removes all items from this hash.

        .. note::

           Under the hood it simply :redis:`DEL` the key.

        """
        self.session.client.delete(self.key)

    def setdefault(self, key, default=None):
        """Sets the given ``default`` value to the ``key``
        if it doesn't exist and then returns the current value
        of the ``key``.

        For example, the following code is::

            val = hash.setdefault('key', 'set this if not exist')

        equivalent to::

            try:
                val = hash['key']
            except KeyError:
                val = hash['key'] = 'set this if not exist'

        except :meth:`setdefault()` method is an atomic operation.

        :param key: the key to get or set
        :param default: the value to be set if the ``key``
                        doesn't exist
        :raises exceptions.TypeError:
           when the given ``key`` is not acceptable by its
           :attr:`key_type` or the given ``default`` value
           is not acceptable by its :attr:`value_type`

        .. note::

           This method internally uses Redis :redis:`HSETNX`
           command which is atomic.

        """
        if self.session.transaction is not None:
            self.session.mark_query()
            try:
                val = self[key]
            except KeyError:
                self.session.mark_manipulative([self.key])
                self[key] = val = default
            return val
        encoded_key = self.key_type.encode(key)
        encoded_val = self.value_type.encode(default)
        result = [None]
        def block(pipe):
            ok = pipe.hsetnx(self.key, encoded_key, encoded_val)
            if ok:
                result[0] = default
            else:
                value = pipe.hget(self.key, encoded_key)
                result[0] = self.value_type.decode(value)
            pipe.multi()
        self.session.client.transaction(block, self.key)
        return result[0]

    @manipulative
    def update(self, mapping={}, **keywords):
        """Updates the hash from the given ``mapping`` and keyword
        arguments.

        - If ``mapping`` has :meth:`~collections.Mapping.keys()`
          method, it does::

              for k in mapping:
                  self[k] = mapping[k]

        - If ``mapping`` lacks :meth:`~collections.Mapping.keys()` 
          method, it does::

              for k, v in mapping:
                  self[k] = v

        - In either case, this is followed by (where ``keywords``
          is a :class:`dict` of keyword arguments)::

              for k, v in keywords.items():
                  self[k] = v

        :param mapping: an iterable object of ``(key, value)``
                        pairs or a mapping object (which has
                        :meth:`~collections.Mapping.keys()`
                        method).  default is empty
        :type mapping: :class:`collections.Mapping`
        :param \*\*keywords: the keywords to update as well.
                             if its :attr:`key_type` doesn't
                             accept byte strings (:class:`str`)
                             it raises :exc:`~exceptions.TypeError`
        :raises exceptions.TypeError:
           if the ``mapping`` is not actually mapping or iterable,
           or the given keys and values to update aren't acceptable
           by its :attr:`key_type` and :attr:`value_type`
        :raises exceptions.ValueError:
           if the ``mapping`` is an iterable object which yields
           non-pair values e.g. ``[(1, 2, 3), (4,)]``

        """
        if isinstance(mapping, Hash):
            mapping = mapping.items()
        value = dict(mapping)
        value.update(keywords)
        pipe = self.session.client
        if self.session.current_transaction is None:
            pipe = pipe.pipeline()
        self._raw_update(value, pipe)
        if self.session.current_transaction is None:
            pipe.execute()

    def _raw_update(self, value, pipe, encoded=False):
        items = getattr(value, 'iteritems', value.items)()
        if encoded:
            flatten = (val for k, v in items for val in (k, v))
        else:
            encode_key = self.key_type.encode
            encode_value = self.value_type.encode
            flatten = (val for k, v in items
                           for val in (encode_key(k), encode_value(v)))
        n = 100  # FIXME: it is an arbitarary magic number.
        for chunk in utils.chunk(flatten, n * 2):
            pipe.execute_command('HMSET', self.key, *chunk)

    def __repr__(self):
        cls = type(self)
        items = list(self.items())
        items.sort(key=lambda elem: elem[0])
        elements = ', '.join('{0!r}: {1!r}'.format(*pair) for pair in items)
        return '<{0}.{1} ({2!r}) {{{3}}}>'.format(cls.__module__, cls.__name__,
                                                  self.key, elements)

