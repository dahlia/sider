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


class SortedSet(collections.Set):
    """The Python-sider representation of Redis sorted set value.
    It behaves in similar way to :class:`collections.Counter` object
    which became a part of standard library since Python 2.7.

    .. table:: Mappings of Redis commands--:class:`SortedSet` methods

       ========================== =============================================
       Redis commands             :class:`SortedSet` methods
       ========================== =============================================
       :redis:`DEL`               :meth:`SortedSet.clear()`
       :redis:`ZADD`              :token:`=` (:meth:`SortedSet.__setitem__()`)
       :redis:`ZCARD`             :func:`len()` (:meth:`SortedSet.__len__()`)
       :redis:`ZINCRBY`           :meth:`SortedSet.update()`
       :redis:`ZRANGE`            :func:`iter()` (:meth:`SortedSet.__iter__()`)
       :redis:`ZRANGE` WITHSCORES :meth:`SortedSet.items()`
       :redis:`ZSCORE`            :meth:`SortedSet.__getitem__()`,
                                  :keyword:`in`
                                  (:meth:`SortedSet.__contains__()`)
       :redis:`ZUNIONSTORE`       :meth:`SortedSet.update()`
       ========================== =============================================

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
        return itertools.imap(self.value_type.decode, result)

    @query
    def __contains__(self, member):
        """:keyword:`in` operator.  Tests whether the set contains
        the given operand ``member``.

        :param member: the value to test
        :returns: ``True`` if the sorted set contains the given
                  operand ``member``
        :rtype: :class:`bool`

        .. note::

           This method internally uses :redis:`ZSCORE` command.

        """
        try:
            element = self.value_type.encode(member)
        except TypeError:
            return False
        return bool(self.session.client.zscore(self.key, element))

    @query
    def __getitem__(self, member):
        """Gets the score of the given ``member``.

        :param member: the member to get its score
        :returns: the score of the ``member``
        :rtype: :class:`numbers.Real`
        :raises exceptions.TypeError:
           if the given ``member`` is not acceptable by
           its :attr:`value_type`
        :raises exceptions.KeyError:
           if there's no such ``member``

        .. note::

           It is directly mapped to Redis :redis:`ZSCORE` command.

        """
        element = self.value_type.encode(member)
        score = self.session.client.zscore(self.key, element)
        if score:
            return score
        raise KeyError(member)

    @manipulative
    def __setitem__(self, member, score):
        """Sets the ``score`` of the ``member``.  Adds the ``member``
        if it doesn't exist.

        :param member: the member to set its ``score``
        :param scorew: the score to set of the ``member``
        :raises exceptions.TypeError:
           if the given ``member`` is not acceptable by
           its :attr:`value_type` or the given ``score``
           is not a :class:`numbers.Real` object

        .. note::

           It is directly mapped to Redis :redis:`ZADD` command.

        """
        if not isinstance(score, numbers.Real):
            raise TypeError('score must be a float, not ' + repr(score))
        element = self.value_type.encode(member)
        self.session.client.zadd(self.key, score, element)

    @query
    def __eq__(self, operand):
        if not isinstance(operand, collections.Sized):
            return False
        length = len(self)
        if length != len(operand):
            return False
        zrange = self.session.client.zrange
        operand_is_sortedset = isinstance(operand, SortedSet)
        if operand_is_sortedset:
            if length == 0:
                return True
            elif self.value_type != operand.value_type:
                return False
        pairs = zrange(self.key, 0, -1, withscores=True)
        decode = self.value_type.decode
        if operand_is_sortedset:
            operand_pairs = zrange(operand.key, 0, -1, withscores=True)
            return pairs == operand_pairs
        elif isinstance(operand, collections.Mapping):
            for element, score in pairs:
                element = decode(element)
                try:
                    s = operand[element]
                except KeyError:
                    return False
                else:
                    if s != score:
                        return False
            return True
        elif isinstance(operand, collections.Set):
            for element, score in pairs:
                if not (score == 1 and decode(element) in operand):
                    return False
            return True
        return False

    def __ne__(self, operand):
        return not (self == operand)

    def keys(self):
        """Gets its all elements.  Equivalent to :meth:`__iter__()`
        except it returns a :class:`~collections.Set` instead of
        iterable.  There isn't any meaningful order of keys.

        :returns: the set of its all keys
        :rtype: :class:`collections.KeysView`

        .. note::

           This method is directly mapped to Redis :redis:`ZRANGE`
           command.

        """
        return frozenset(self)

    @query
    def items(self):
        """Returns a set of pairs of elements and these scores.

        :returns: a set of pairs.  every pair looks like (element, score)
        :rtype: :class:`collections.ItemsView`

        .. note::

           This method is directly mapped to :redis:`ZRANGE`
           command and ``WITHSCORES`` option.

        """
        pairs = self.session.client.zrange(self.key, 0, -1, withscores=True)
        decode = self.value_type.decode
        return frozenset((decode(value), score) for value, score in pairs)

    @query
    def values(self):
        """Returns a list of scores in ascending order.

        :returns: a list of scores in ascending order
        :rtype: :class:`collections.ValuesView`

        .. note::

           This method internally uses :redis:`ZRANGE` command.

        """
        pairs = self.session.client.zrange(self.key, 0, -1, withscores=True)
        return [score for _, score in pairs]

    @manipulative
    def clear(self):
        """Removes all values from this sorted set.

        .. note::

           Under the hood it simply :redis:`DEL` the key.

        """
        self.session.client.delete(self.key)

    def update(self, *sets, **keywords):
        """Merge with passed sets and keywords.  It's behavior is
        almost equivalent to :meth:`dict.update()` and
        :meth:`set.update()` except it's aware of scores.

        For example, assume the initial elements and their scores of
        the set is (in notation of dictionary)::

            {'c': 1, 'a': 2, 'b': 3}

        and you has updated it::

            sortedset.update(set('acd'))

        then it becomes (in notation of dictionary)::

            {'d': 1, 'c': 2, 'a': 3, 'b': 3}

        You can pass mapping objects or keywords instead to specify
        scores to increment::

            sortedset.update({'a': 1, 'b': 2})
            sortedset.update(a=1, b=2)
            sortedset.update(set('ab'), set('cd'),
                             {'a': 1, 'b': 2}, {'c': 1, 'd': 2},
                             a=1, b=2, c=1, d=2)

        :param \*sets: sets or mapping objects to merge with.
                       mapping objects can specify scores by values
        :param \**keywords: if :attr:`value_type` takes byte strings
                            you can specify elements and its scores
                            by keyword arguments

        .. note::

           There's an incompatibility with :meth:`dict.update()`.
           It always treats iterable of pairs as set of pairs, not
           mapping pairs, unlike :meth:`dict.update()`.  It is for
           resolving ambiguity (remember :attr:`value_type` can take
           tuples or such things).

        .. note::

           Under the hood it uses multiple :redis:`ZINCRBY` commands
           and :redis:`ZUNIONSTORE` if there are one or more
           :class:`SortedSet` objects in operands.

        """
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
                if not isinstance(score, numbers.Real):
                    raise TypeError('score must be a float, not ' +
                                    repr(score))
                el = encode(el)
                zincrby(key, value=el, amount=score)
            if online_sets:
                keys = [set_.key for set_ in online_sets]
                session.client.zunionstore(key, len(keys) + 1, key, *keys)
        session.transaction(block, [key], ignore_double=True)

    def __repr__(self):
        cls = type(self)
        pairs= list(self.items())
        pairs.sort(key=lambda (element, score): (score, element))
        elements = ', '.join(repr(v) if s == 1 else '{0!r}: {1!r}'.format(v, s)
                             for v, s in pairs)
        return '<{0}.{1} ({2!r}) {{{3}}}>'.format(cls.__module__, cls.__name__,
                                                  self.key, elements)

