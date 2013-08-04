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
from .types import Bulk, String
from .transaction import query, manipulative


class SortedSet(collections.MutableMapping, collections.MutableSet):
    """The Python-sider representation of Redis sorted set value.
    It behaves in similar way to :class:`collections.Counter` object
    which became a part of standard library since Python 2.7.

    It implements :class:`collections.MutableMapping` and
    :class:`collections.MutableSet` protocols.

    .. table:: Mappings of Redis commands--:class:`SortedSet` methods

       ========================== ==================================
       Redis commands             :class:`SortedSet` methods
       ========================== ==================================
       :redis:`DEL`               :meth:`SortedSet.clear()`
       :redis:`ZADD`              :token:`=`
                                  (:meth:`SortedSet.__setitem__()`)
       :redis:`ZCARD`             :func:`len()`
                                  (:meth:`SortedSet.__len__()`)
       :redis:`ZINCRBY`           :meth:`SortedSet.add()`,
                                  :meth:`SortedSet.discard()`,
                                  :meth:`SortedSet.update()`
       :redis:`ZRANGE`            :func:`iter()`
                                  (:meth:`SortedSet.__iter__()`)
       :redis:`ZRANGE` WITHSCORES :meth:`SortedSet.items()`,
                                  :meth:`SortedSet.most_common()`,
                                  :meth:`SortedSet.least_common()`
       :redis:`ZREM`              :keyword:`del`
                                  (:meth:`SortedSet.__delitem__()`),
                                  :meth:`SortedSet.discard()`
       :redis:`ZSCORE`            :meth:`SortedSet.__getitem__()`,
                                  :keyword:`in`
                                  (:meth:`SortedSet.__contains__()`)
       :redis:`ZUNIONSTORE`       :meth:`SortedSet.update()`
       N/A                        :meth:`SortedSet.setdefault()`
       N/A                        :meth:`SortedSet.pop()`
       N/A                        :meth:`SortedSet.popitem()`
       ========================== ==================================

    .. todo::

       - Implement :meth:`issuperset()` method.
       - Implement :meth:`issubset()` method.
       - Implement :meth:`isdisjoint()` method.
       - Implement :meth:`union()` method.
       - Implement :meth:`intersection()` method.
       - Implement :meth:`intersection_update()` using :redis:`ZINTERSTORE`.
       - Implement :meth:`difference()` method.
       - Implement :meth:`difference_update()` method.
       - Implement :meth:`subtract()` method.

    """

    #: (:class:`sider.types.Bulk`) The type of set elements.
    value_type = None

    def __init__(self, session, key, value_type=String):
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
        for i in result:
            yield self.value_type.decode(i)

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
        return self.session.client.zscore(self.key, element) is not None

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
        if score is None:
            raise KeyError(member)
        return score

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

    def __delitem__(self, member):
        """Removes the ``member``.

        :param member: the member to delete
        :raises exceptions.TypeError:
           if the given ``member`` is not acceptable by
           its :attr:`value_type`
        :raises exceptions.KeyError:
           if there's no such ``member``

        .. note::

           It is directly mapped to Redis :redis:`ZREM` command
           when it's not on transaction.  If it's used with
           transaction, it internally uses :redis:`ZSCORE` and
           :redis:`ZREM` commands.

        """
        element = self.value_type.encode(member)
        session = self.session
        if session.current_transaction is None:
            exists = session.client.zrem(self.key, element)
        else:
            session.mark_query()
            exists = session.client.zscore(self.key, element) is not None
            if exists:
                session.mark_manipulative()
                session.client.zrem(self.key, element)
        if not exists:
            raise KeyError(member)

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

    def keys(self, reverse=False):
        """Gets its all elements.  Equivalent to :meth:`__iter__()`
        except it returns an ordered :class:`~collections.Sequence`
        instead of iterable.

        :param reverse: order result descendingly if it's ``True``.
                        default is ``False`` which means ascending order
        :type reverse: :class:`bool`
        :returns: the ordered list of its all keys
        :rtype: :class:`collections.Sequence`

        .. note::

           This method is directly mapped to Redis :redis:`ZRANGE`
           command.

        """
        client = self.session.client
        zrange = client.zrevrange if reverse else client.zrange
        decode = self.value_type.decode
        return map(decode, zrange(self.key, 0, -1))

    @query
    def items(self, reverse=False):
        """Returns an ordered of pairs of elements and these scores.

        :param reverse: order result descendingly if it's ``True``.
                        default is ``False`` which means ascending order
        :type reverse: :class:`bool`
        :returns: an ordered list of pairs.
                  every pair looks like (element, score)
        :rtype: :class:`collections.Sequence`

        .. note::

           This method is directly mapped to :redis:`ZRANGE`
           command and ``WITHSCORES`` option.

        """
        return self.least_common(reverse=reverse)

    @query
    def values(self, reverse=False):
        """Returns an ordered list of scores.

        :param reverse: order result descendingly if it's ``True``.
                        default is ``False`` which means ascending order
        :type reverse: :class:`bool`
        :returns: an ordered list of scores
        :rtype: :class:`collections.Sequence`

        .. note::

           This method internally uses :redis:`ZRANGE` command
           and ``WITHSCORES`` option.

        """
        client = self.session.client
        zrange = client.zrevrange if reverse else client.zrange
        pairs = zrange(self.key, 0, -1, withscores=True)
        return [score for _, score in pairs]

    def most_common(self, n=None, reverse=False):
        """Returns a list of the ``n`` most common (exactly, highly
        scored) members and their counts (scores) from the most
        common to the least.  If ``n`` is not specified, it returns
        *all* members in the set.  Members with equal scores are
        ordered arbitarily.

        :param n: the number of members to get
        :type n: :class:`numbers.Integral`
        :returns: an ordered list of pairs.
                  every pair looks like (element, score)
        :rtype: :class:`collections.Sequence`

        .. note::

           This method is directly mapped to :redis:`ZRANGE`
           command and ``WITHSCORES`` option.

        """
        return self.least_common(n, reverse=not reverse)

    @query
    def least_common(self, n=None, reverse=False):
        """Returns a list of the ``n`` least common (exactly, lowly
        scored) members and their counts (scores) from the least
        common to the most.  If ``n`` is not specified, it returns
        *all* members in the set.  Members with equal scores are
        ordered arbitarily.

        :param n: the number of members to get
        :type n: :class:`numbers.Integral`
        :returns: an ordered list of pairs.
                  every pair looks like (element, score)
        :rtype: :class:`collections.Sequence`

        .. note::

           This method is directly mapped to :redis:`ZREVRANGE`
           command and ``WITHSCORES`` option.

        """
        if n is None:
            n = 0
        elif not isinstance(n, numbers.Integral):
            raise TypeError('n must be an integer, not ' + repr(n))
        client = self.session.client
        zrange = client.zrevrange if reverse else client.zrange
        pairs = zrange(self.key, 0, n - 1, withscores=True)
        decode = self.value_type.decode
        return [(decode(value), score) for value, score in pairs]

    @manipulative
    def add(self, member, score=1):
        """Adds a new ``member`` or increases its ``score`` (default is 1).

        :param member: the member to add or increase its score
        :param score: the amount to increase the score.  default is 1
        :type score: :class:`numbers.Real`

        .. note::

           This method is directly mapped to :redis:`ZINCRBY` command.

        """
        if not isinstance(score, numbers.Real):
            raise TypeError('score must be a numbers.Real, not ' + repr(score))
        element = self.value_type.encode(member)
        self.session.client.zincrby(self.key, value=element, amount=score)

    def discard(self, member, score=1, remove=0):
        """Opposite operation of :meth:`add()`.  It decreases
        its ``score`` (default is 1).  When its score get the
        ``remove`` number (default is 0) or less, it will be removed.

        If you don't want to remove it but only decrease its
        score, pass ``None`` into ``remove`` parameter.

        If you want to remove ``member``, not only decrease its
        score, use :meth:`__delitem__()` instead::

            del sortedset[member]

        :param member: the member to decreases its score
        :param score: the amount to decrease the score.  default is 1
        :type score: :class:`numbers.Real`
        :param remove: the threshold score to be removed.
                       if ``None`` is passed, it doesn't remove
                       the member but only decreases its score
                       (it makes ``score`` argument meaningless).
                       default is 0.
        :type remove: :class:`numbers.Real`

        .. note::

           This method is directly mapped to :redis:`ZINCRBY` command
           when ``remove`` is ``None``.

           Otherwise, it internally uses :redis:`ZSCORE` plus
           :redis:`ZINCRBY` or `:redis:`ZREM` (total two commands)
           within a transaction.

        """
        if not isinstance(score, numbers.Real):
            raise TypeError('score must be a numbers.Real, not ' + repr(score))
        elif not (remove is None or isinstance(remove, numbers.Real)):
            raise TypeError('remove must be a numbers.Real, not ' +
                            repr(score))
        if remove is None:
            self.add(member, -score)
            return
        element = self.value_type.encode(member)
        def block(trial, transaction):
            pipe = self.session.client
            self.session.mark_query()
            current = pipe.zscore(self.key, element)
            if current is None:
                return
            self.session.mark_manipulative()
            if current - score > remove:
                pipe.zincrby(self.key, value=element, amount=-score)
            else:
                pipe.zrem(self.key, element)
        self.session.transaction(block, [self.key], ignore_double=True)

    def setdefault(self, key, default=1):
        """Gets the score of the given ``key`` if it exists or
        adds ``key`` with ``default`` score.

        :param key: the member to get its score
        :param default: the score to be set if the ``key`` doesn't
                        exist.  default is 1
        :type default: :class:`numbers.Real`
        :returns: the score of the ``key`` after the operation
                  has been committed
        :rtype: :class:`numbers.Real`

        .. note::

           It internally uses one or two commands.
           At first it sends :redis:`ZSCORE` command to check
           whether the key exists and get its score if it exists.
           If it doesn't exist yet, it sends one more command:
           :redis:`ZADD`.  It is atomically committed
           in a transaction.

        """
        if not isinstance(default, numbers.Real):
            raise TypeError('default must be a numbera.Real value, not ' +
                            repr(default))
        element = self.value_type.encode(key)
        score = [None]
        def block(trial, transaction):
            pipe = self.session.client
            self.session.mark_query()
            score[0] = pipe.zscore(self.key, element)
            if score[0] is None:
                self.session.mark_manipulative()
                pipe.zadd(self.key, default, element)
        self.session.transaction(block, [self.key], ignore_double=True)
        if score[0] is None:
            return default
        return score[0]

    def popitem(self, desc=False, score=1, remove=0):
        """Populates the lowest scored member (or the highest
        if ``desc`` is ``True``) and its score.

        It returns a pair of the populated member and its score.
        The score is a value before the operation has been
        committed.

        :param desc: by default, it populates the member of
                     the lowest score, but if you pass ``True``
                     to this parameter it will populates
                     the highest instead.  default is ``False``
        :type desc: :class:`bool`
        :param score: the amount to decrease the score.
                      default is 1
        :type score: :class:`numbers.Real`
        :param remove: the threshold score to be removed.
                       if ``None`` is passed, it doesn't remove
                       the member but only decreases its score
                       (it makes ``score`` argument meaningless).
                       default is 0.
        :type remove: :class:`numbers.Real`
        :returns: a pair of the populated member and its score.
                  the first part of a pair will be the lowest
                  scored member or the highest scored member
                  if ``desc`` is ``True``.  the second part of
                  a pair will be the score before the operation
                  has been committed
        :rtype: :class:`tuple`
        :raises exceptions.KeyError: when the set is empty

        .. note::

           It internally uses :redis:`ZRANGE` or :redis:`ZREVRANGE`,
           :redis:`ZREM` or :redis:`ZINCRBY` (total 2 commands)
           in a transaction.

        .. seealso::

           Method :meth:`pop()`

        """
        resultset = []
        def block(trial, transaction):
            pipe = self.session.client
            zrange = pipe.zrevrange if desc else pipe.zrange
            self.session.mark_query()
            resultset[:] = zrange(self.key, 0, 0, withscores=True)
            if resultset:
                self.session.mark_manipulative()
                if remove is None or resultset[0][1] - score <= remove:
                    pipe.zrem(self.key, resultset[0][0])
                else:
                    pipe.zincrby(self.key,
                                 value=resultset[0][0],
                                 amount=-score)
            else:
                raise KeyError('pop from an empty set')
        self.session.transaction(block, [self.key], ignore_double=True)
        value, score = resultset[0]
        return self.value_type.decode(value), score

    def pop(self, *args, **kwargs):
        """Populates a member of the set.

        If ``key`` keyword argument or one or more positional
        arguments have present, it behaves like :meth:`dict.pop()`
        method:

        :param key: the member to populate.  it will be removed if
                    it exists
        :param default: the default value returned instead of the
                        member (``key``) when it doesn't exist.
                        default is ``None``
        :returns: the score of the member before the operation
                  has been committed
        :rtype: :class:`numbers.Real`

        .. note::

           It internally uses :redis:`ZSCORE`, :redis:`ZREM` or
           :redis:`ZINCRBY` (total 2 commands) in a transaction.

        If no positional arguments or no ``key`` keyword argument,
        it behaves like :meth:`set.pop()` method.  Basically it
        does the same thing with :meth:`popitem()` except it
        returns just a popped value (while :meth:`popitem()`
        returns a pair of popped value and its score).

        :param desc: keyword only.  by default, it populates
                     the member of the lowest score, but if you
                     pass ``True`` to this it will populates
                     the highest instead.  default is ``False``
        :type desc: :class:`bool`
        :returns: the populated member.  it will be the lowest
                  scored member or the highest scored member
                  if ``desc`` is ``True``
        :raises exceptions.KeyError: when the set is empty

        .. note::

           It internally uses :redis:`ZRANGE` or :redis:`ZREVRANGE`,
           :redis:`ZREM` or :redis:`ZINCRBY` (total 2 commands)
           in a transaction.

        .. seealso::

           Method :meth:`popitem()`

        If any case there are common keyword-only parameters:

        :param score: keyword only.  the amount to decrease
                      the score.  default is 1
        :type score: :class:`numbers.Real`
        :param remove: keyword only.
                       the threshold score to be removed.
                       if ``None`` is passed, it doesn't remove
                       the member but only decreases its score
                       (it makes ``score`` argument meaningless).
                       default is 0.
        :type remove: :class:`numbers.Real`

        """
        score = kwargs.pop('score', 1)
        remove = kwargs.pop('remove', 0)
        ar_len = len(args)
        kw_len = len(kwargs)
        kw_desc = 'desc' in kwargs
        kw_key = 'key' in kwargs
        kw_default = 'default' in kwargs
        if not args and (not kwargs or kw_len == 1 and kw_desc):
            pair = self.popitem(*args, score=score, remove=remove, **kwargs)
            return pair[0]
        elif (not args and kw_len == 2 and kw_key and kw_default or
              ar_len == 1 and (not kwargs or kw_len == 1 and kw_default) or
              ar_len == 2):
            if ar_len == 2:
                key, default = args
            elif ar_len == 1:
                key = args[0]
                default = kwargs.get('default')
            else:
                key = kwargs['key']
                default = kwargs.get('default')
            element = self.value_type.encode(key)
            current = [None]
            def block(trial, transaction):
                pipe = self.session.client
                self.session.mark_query()
                current[0] = pipe.zscore(self.key, element)
                if current[0] is not None:
                    self.session.mark_manipulative()
                    if remove is None or current[0] - score <= remove:
                        pipe.zrem(self.key, element)
                    else:
                        pipe.zincrby(self.key, value=element, amount=-score)
            self.session.transaction(block, [self.key], ignore_double=True)
            if current[0] is None:
                return default
            return current[0]
        elif kw_desc and (args or kw_key):
            raise TypeError('desc option cannot be applied with key '
                            'parameter at a time')
        elif not args and not kw_key and kw_default:
            raise TypeError('default option must be used with key argument')
        else:
            raise TypeError('invalid argument(s)')

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
            for el, score in getattr(keywords, 'iteritems', keywords.items)():
                if not isinstance(score, numbers.Real):
                    raise TypeError('score must be a float, not ' +
                                    repr(score))
                el = encode(el)
                zincrby(key, value=el, amount=score)
            if online_sets:
                keys = [set_.key for set_ in online_sets]
                keys.insert(0, key)
                session.client.zunionstore(key, keys)
        session.transaction(block, [key], ignore_double=True)

    def __repr__(self):
        cls = type(self)
        pairs= list(self.items())
        pairs.sort(key=lambda pair: (pair[1], pair[0]))
        elements = ', '.join(repr(v) if s == 1 else '{0!r}: {1!r}'.format(v, s)
                             for v, s in pairs)
        return '<{0}.{1} ({2!r}) {{{3}}}>'.format(cls.__module__, cls.__name__,
                                                  self.key, elements)

