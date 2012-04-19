""":mod:`sider.sortedset` --- Sorted sets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. seealso::

    `Redis Data Types <http://redis.io/topics/data-types>`_
       The Redis documentation that explains about its data
       types: strings, lists, sets, sorted sets and hashes.

"""
import numbers
import collections
import itertools
from .session import Session
from .types import Bulk, ByteString
from .transaction import query, manipulative


class SortedSet(collections.Sized, collections.Iterable):
    """The Python-sider representaion of Redis sorted set value.
    It behaves in similar way to :class:`collections.Counter` object
    which became a part of standard library since Python 2.7.

    .. table:: Mappings of Redis commands--:class:`SortedSet` methods

       ===================== =============================================
       Redis commands        :class:`SortedSet` methods
       ===================== =============================================
       :redis:`ZCARD`        :func:`len()` (:meth:`SortedSet.__len__()`)
       :redis:`ZRANGE`       :func:`iter()` (:meth:`SortedSet.__iter__()`)
       ===================== =============================================

    """

    #: (:class:`sider.types.Bulk`) The type of set elements.
    value_type = None

    def __init__(self, session, key, value_type=ByteString):
        if not isinstance(session, Session):
            raise TypeError('session must be a sider.session.Session '
                            'instance, not ' + repr(session))
        self.session = session
        self.key = key
        self.value_type = Bulk.ensure_value_type(value_type,
                                                 parameter='value_type')

    @query
    def __len__(self):
        """Gets the cardinality of the sorted set.

        :returns: the cardinality (the number of elements)
                  of the sorted set
        :rtype: :class:`numbers.Integral`

        .. note::

           It is directly mapped to Redis :redis:`ZCARD` command.

        """
        return self.session.client.zcard(self.key)

    @query
    def __iter__(self):
        result = self.session.client.zrange(self.key, 0, -1)
        return itertools.imap(self.value_type.encode, result)

    @manipulative
    def clear(self):
        """Removes all values from this sorted set.

        .. note::

           Under the hood it simply :redis:`DEL` the key.

        """
        self.session.client.delete(self.key)

    def update(self, *sets, **keywords):
        """Very complicated operation.  Should be documented."""
        session = self.session
        key = self.key
        encode = self.value_type.encode
        def block(trial, transaction):
            session.mark_manipulative([key])
            zincrby = session.client.zincrby
            online_sets = []
            for set_ in sets:
                if isinstance(set_, SortedSet):
                    online_sets.append(set_)
                elif isinstance(set_, collections.Mapping):
                    for el, score in getattr(set_, 'iteritems', set_.items)():
                        el = encode(el)
                        if not isinstance(score, numbers.Real):
                            raise TypeError('score must be a float, not ' +
                                            repr(score))
                        zincrby(key, value=el, amount=score)
                elif isinstance(set_, collections.Iterable):
                    for el in set_:
                        el = encode(el)
                        zincrby(key, value=el, amount=1)
                else:
                    raise TypeError('expected iterable, not ' + repr(set_))
            for el, score in keywords.iteritems():
                if not isinstance(score, numbers.Integral):
                    raise TypeError('score must be integer, not ' +
                                    repr(score))
                el = encode(el)
                zincrby(key, value=el, amount=score)
            if online_sets:
                keys = [set_.key for set_ in online_sets]
                session.client.zunionstore(key, len(keys) + 1, key, *keys)
        session.transaction(block, [key], ignore_double=True)

