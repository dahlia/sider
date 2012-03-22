""":mod:`sider.set` --- Set objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from __future__ import absolute_import
import collections
from .session import Session
from .types import Bulk, ByteString


class Set(collections.MutableSet):
    """The Python-side representaion of Redis set value.  It behaves
    alike built-in Python :class:`set` object.  More exactly, it
    implements :class:`collections.MutableSet` protocol.

    ==================== ======================================================
    Redis command        :class:`Set` methods
    ==================== ======================================================
    :redis:`SADD`        :meth:`Set.add()`,
                         :meth:`Set.update()`
    :redis:`SCARD`       :func:`len()` (:meth:`Set.__len__()`)
    :redis:`SDIFF`       :meth:`Set.difference()`,
                         :token:`-` (:meth:`Set.__sub__()`)
    :redis:`SDIFFSTORE`  :meth:`Set.difference_update()`,
                         :token:`-=` (:meth:`Set.__isub__()`)
    :redis:`SINTER`      :meth:`Set.intersection()`,
                         :token:`&` (:meth:`Set.__and__()`)
    :redis:`SINTERSTORE` :meth:`Set.intersection_update()`,
                         :token:`&=` (:meth:`Set.__iand__()`)
    :redis:`SISMEMBER`   :keyword:`in` (:meth:`Set.__contains__()`)
    :redis:`SMEMBERS`    :func:`iter()` (:meth:`Set.__iter__()`)
    :redis:`SMOVE`       N/A
    :redis:`SPOP`        :meth:`Set.pop()`
    :redis:`SRANDMEMBER` N/A
    :redis:`SREM`        :meth:`Set.discard()`,
                         :meth:`Set.remove()`
    :redis:`SUNION`      :meth:`Set.union()`,
                         :token:`|` (:meth:`Set.__or__()`)
    :redis:`SUNIONSTORE` :meth:`Set.update()`,
                         :token:`|=` (:meth:`Set.__ior__()`)
    N/A                  :meth:`Set.symmetric_difference()`,
                         :token:`^` (:meth:`Set.__xor__()`)
    N/A                  :meth:`Set.symmetric_difference_update()`,
                         :token:`^=` (:meth:`Set.__ixor__()`)
    ==================== ======================================================

    """

    def __init__(self, session, key, value_type=ByteString):
        if not isinstance(session, Session):
            raise TypeError('session must be a sider.session.Session '
                            'instance, not ' + repr(session))
        self.session = session
        self.key = key
        self.value_type = Bulk.ensure_value_type(value_type,
                                                 parameter='value_type')

    def __iter__(self):
        decode = self.value_type.decode
        for member in self.session.client.smembers(self.key):
            yield decode(member)

    def __len__(self):
        """Gets the cardinality of the set.

        Use this with the built-in :func:`len()` function.

        :returns: the cardinality of the set
        :rtype: :class:`numbers.Integral`

        .. note::

           This method is directly mapped to :redis:`SCARD`
           command.

        """
        return self.session.client.scard(self.key)

    def __contains__(self, member):
        """:keyword:`in` operator.  Tests whether the set contains
        the given operand ``member``.

        :param member: the value to test
        :returns: ``True`` if the set contains the given
                  operand ``member``
        :rtype: :class:`bool`

        .. note::

           This method is directly mapped to :redis:`SISMEMBER`
           command.

        """
        try:
            data = self.value_type.encode(member)
        except TypeError:
            return False
        return bool(self.session.client.sismember(self.key, data))

    def __eq__(self, operand):
        if isinstance(operand, collections.Set):
            return frozenset(self) == frozenset(operand)
        return False

    def __ne__(self, operand):
        return not (self == operand)

    def __lt__(self, operand):
        """Less-than (:token:`<`) operator.  Tests whether the set is
        a *proper* (or *strict*) subset of the given ``operand`` or not.

        To eleborate, the key difference between this less-than
        (:token:`<`) operator and less-than or equal-to (:token:`<=`)
        operator, which is equivalent to :meth:`issubset()` method,
        is that it returns ``False`` even if two sets are exactly
        the same.

        Let this show a simple example:

        .. sourcecode:: pycon

           >>> assert isinstance(s, sider.set.Set)  # doctest: +SKIP
           >>> set(s)  # doctest: +SKIP
           set([1, 2, 3])
           >>> s < set([1, 2]), s <= set([1, 2])  # doctest: +SKIP
           (False, False)
           >>> s < set([1, 2, 3]), s <= set([1, 2, 3])  # doctest: +SKIP
           (False, True)
           >>> s < set([1, 2, 3, 4]), s <= set([1, 2, 3, 4]) # doctest: +SKIP
           (True, True)

        :param operand: another set to test
        :type operand: :class:`collections.Set`
        :returns: ``True`` if the set is a proper subset of ``operand``
        :rtype: :class:`bool`

        """
        if not isinstance(operand, collections.Set):
            raise TypeError('operand for < must be an instance of '
                            'collections.Set, not ' + repr(operand))
        if (isinstance(operand, Set) and self.session is operand.session and
            self.value_type == operand.value_type):
            client = self.session.client
            for _ in client.sdiff(self.key, operand.key):
                return False
            card = len(self)
            if card != len(client.sinter(self.key, operand.key)):
                return False
            return card < client.scard(operand.key)
        return frozenset(self) < frozenset(operand)

    def __le__(self, operand):
        """Less-than or equal to (:token:`<=`) operator.
        Tests whether the set is a subset of the given ``operand``.

        It's the same operation to :meth:`issubset()` method except
        it can take a set-like operand only.  On the other hand
        :meth:`issubset()` can take an any iterable operand as well.

        :param operand: another set to test
        :type operand: :class:`collections.Set`
        :returns: ``True`` if the ``operand`` set contains the set
        :rtype: :class:`bool`

        """
        if not isinstance(operand, collections.Set):
            raise TypeError('operand for <= must be an instance of '
                            'collections.Set, not ' + repr(operand))
        return self.issubset(operand)

    def __gt__(self, operand):
        """Greater-than (:token:`>`) operator.  Tests whether the set
        is a *proper* (or *strict*) superset of the given ``operand``.

        To eleborate, the key difference between this greater-than
        (:token:`>`) operator and greater-than or equal-to
        (:token:`>=`) operator, which is equivalent to
        :meth:`issuperset()` method, is that it returns ``False``
        even if two sets are exactly the same.

        Let this show a simple example:

        .. sourcecode:: pycon

           >>> assert isinstance(s, sider.set.Set)  # doctest: +SKIP
           >>> set(s)  # doctest: +SKIP
           set([1, 2, 3])
           >>> s > set([1, 2]), s >= set([1, 2])  # doctest: +SKIP
           (True, True)
           >>> s > set([1, 2, 3]), s >= set([1, 2, 3])  # doctest: +SKIP
           (False, True)
           >>> s > set([1, 2, 3, 4]), s >= set([1, 2, 3, 4]) # doctest: +SKIP
           (False, False)

        :param operand: another set to test
        :type operand: :class:`collections.Set`
        :returns: ``True`` if the set is a proper superset of
                  ``operand``
        :rtype: :class:`bool`

        """
        if not isinstance(operand, collections.Set):
            raise TypeError('operand for > must be an instance of '
                            'collections.Set, not ' + repr(operand))
        if isinstance(operand, Set):
            return operand < self
        return frozenset(self) > frozenset(operand)

    def __ge__(self, operand):
        """Greater-than or equal to (:token:`>=`) operator.
        Tests whether the set is a superset of the given ``operand``.

        It's the same operation to :meth:`issuperset()` method except
        it can take a set-like operand only.  On the other hand
        :meth:`issuperset()` can take an any iterable operand as well.

        :param operand: another set to test
        :type operand: :class:`collections.Set`
        :returns: ``True`` if the set contains the ``operand``
        :rtype: :class:`bool`

        """
        if not isinstance(operand, collections.Set):
            raise TypeError('operand for >= must be an instance of '
                            'collections.Set, not ' + repr(operand))
        return self.issuperset(operand)

    def __sub__(self, operand):
        """Minus (:token:`-`) operator.  Gets the relative complement
        of the ``operand`` in the set.

        Mostly equivalent to :meth:`difference()` method except it
        can take a set-like operand only.  On the other hand
        :meth:`difference()` can take an any iterable operand as well.

        :param operand: another set to get the relative complement
        :type operand: :class:`collections.Set`
        :returns: the relative complement
        :rtype: :class:`set`

        """
        if not isinstance(operand, collections.Set):
            raise TypeError('operand for - must be an instance of '
                            'collections.Set, not ' + repr(operand))
        return self.difference(operand)

    def __rsub__(self, operand):
        if not isinstance(operand, collections.Set):
            raise TypeError('operand for - must be an instance of '
                            'collections.Set, not ' + repr(operand))
        elif isinstance(operand, (Set, set, frozenset)):
            return operand.difference(self)
        operand = set(operand)
        operand.difference_update(self)
        return operand

    def __xor__(self, operand):
        """Bitwise exclusive or (:token:`^`) operator.
        Returns a new set with elements in either the set or
        the ``operand`` but not both.

        Mostly equivalent to :meth:`symmetric_difference()` method
        except it can take a set-like operand only.  On the other hand
        :meth:`symmetric_difference()` can take an any iterable
        operand as well.

        :param operand: other set
        :type operand: :class:`collections.Set`
        :returns: a new set with elements in either the set or
                  the ``operand`` but not both
        :rtype: :class:`set`

        """
        if not isinstance(operand, collections.Set):
            raise TypeError('operand for ^ must be an instance of '
                            'collections.Set, not ' + repr(operand))
        return self.symmetric_difference(operand)

    def __rxor__(self, operand):
        if not isinstance(operand, collections.Set):
            raise TypeError('operand for ^ must be an instance of '
                            'collections.Set, not ' + repr(operand))
        return self.symmetric_difference(operand)

    def __or__(self, operand):
        """Bitwise or (:token:`|`) operator.  Gets the union of
        operands.

        Mostly equivalent to :meth:`union()` method except it can
        take only one set-like operand.  On the other hand
        :meth:`union()` can take zero or more iterable operands
        (not only set-like objects).

        :param operand: another set to union
        :type operand: :class:`collections.Set`
        :returns: the union set
        :rtype: :class:`set`

        """
        if not isinstance(operand, collections.Set):
            raise TypeError('operand for | must be an instance of '
                            'collections.Set, not ' + repr(operand))
        return self.union(operand)

    def __ror__(self, operand):
        return self | operand

    def __ior__(self, operand):
        """Bitwise or (:token:`|=`) assignment.  Updates the set
        with the union of itself and the ``operand``.

        Mostly equivalent to :meth:`update()` method except it can
        take only one set-like operand.  On the other hand
        :meth:`update()` can take zero or more iterable operands
        (not only set-like objects).

        :param operand: another set to union
        :type operand: :class:`collections.Set`
        :returns: the set itself
        :rtype: :class:`Set`

        """
        if not isinstance(operand, collections.Set):
            raise TypeError('operand for |= must be an instance of '
                            'collections.Set, not ' + repr(operand))
        self.update(operand)
        return self

    def __and__(self, operand):
        """Bitwise and (:token:`&`) operator.  Gets the union of
        operands.

        Mostly equivalent to :meth:`intersection()` method except it
        can take only one set-like operand.  On the other hand
        :meth:`intersection()` can take zero or more iterable
        operands (not only set-like objects).

        :param operand: another set to get intersection
        :type operand: :class:`collections.Set`
        :returns: the intersection
        :rtype: :class:`set`

        """
        if not isinstance(operand, collections.Set):
            raise TypeError('operand for & must be an instance of '
                            'collections.Set, not ' + repr(operand))
        return self.intersection(operand)

    def __rand__(self, operand):
        return self & operand

    def issubset(self, operand):
        """Tests whether the set is a subset of the given ``operand`` or not.
        To test proper (strict) subset, use :token:`<` operator instead.

        :param operand: another set to test
        :type operand: :class:`collections.Iterable`
        :returns: ``True`` if the ``operand`` set contains the set
        :rtype: :class:`bool`

        .. note::

           This method consists of following Redis commands:

           1. :redis:`SDIFF` for this set and ``operand``
           2. :redis:`SLEN` for this set
           3. :redis:`SLEN` for ``operand``

           If the first :redis:`SDIFF` returns anything, it sends
           no commands of the rest and simply returns ``False``.

        """
        if (isinstance(operand, Set) and self.session is operand.session and
            self.value_type == operand.value_type):
            client = self.session.client
            for _ in client.sdiff(self.key, operand.key):
                return False
            return len(self) == len(client.sinter(self.key, operand.key))
        return frozenset(self).issubset(operand)

    def issuperset(self, operand):
        """Tests whether the set is a superset of the given
        ``operand``.  To test proper (strict) superset,
        use :token:`>` operator instead.

        :param operand: another set to test
        :type operand: :class:`collections.Iterable`
        :returns: ``True`` if the set contains ``operand``
        :rtype: :class:`bool`

        """
        if isinstance(operand, (Set, set, frozenset)):
            return operand.issubset(self)
        return frozenset(self).issuperset(operand)

    def isdisjoint(self, operand):
        """Tests whether two sets are disjoint or not.

        :param operand: another set to test
        :type operand: :class:`collections.Iterable`
        :returns: ``True`` if two sets have a null intersection
        :rtype: :class:`bool`

        .. note::

           It internally uses :redis:`SINTER` command.

        """
        if isinstance(operand, Set) and self.session is operand.session:
            if self.value_type != operand.value_type:
                return True
            for _ in self.session.client.sinter(self.key, operand.key):
                return False
            return True
        dec = self.value_type.decode
        return super(Set, self).isdisjoint(dec(member) for member in operand)

    def difference(self, operand):
        """Gets the relative complement of the ``operand`` set in the set.

        :param operand: another set to get the relative complement
        :type operand: :class:`collections.Iterable`
        :returns: the relative complement
        :rtype: :class:`set`

        .. note::

           This method is mapped to :redis:`SDIFF` command.

        """
        if isinstance(operand, Set) and self.session is operand.session:
            if self.value_type != operand.value_type:
                return set(self)
            diff = self.session.client.sdiff(self.key, operand.key)
            decode = self.value_type.decode
            return set(decode(member) for member in diff)
        return set(self).difference(operand)

    def symmetric_difference(self, operand):
        """Returns a new set with elements in either the set or
        the ``operand`` but not both.

        :param operand: other set
        :type operand: :class:`collections.Iterable`
        :returns: a new set with elements in either the set or
                  the ``operand`` but not both
        :rtype: :class:`set`

        .. note::

           This method consists of following two commands:

           1. :redis:`SUNION` of this set and the ``operand``
           2. :redis:`SINTER` of this set and the ``operand``

           and then makes a new :class:`set` with elements in
           the first result are that are not in the second result.

        """
        if (isinstance(operand, Set) and self.session is operand.session and
            self.value_type == operand.value_type):
            union = self.session.client.sunion(self.key, operand.key)
            inter = self.session.client.sinter(self.key, operand.key)
            symdiff = set(union)
            symdiff.difference_update(inter)
            decode = self.value_type.decode
            return set(decode(member) for member in symdiff)
        return set(self).symmetric_difference(operand)

    def union(self, *sets):
        """Gets the union of the given sets.

        :param \*sets: zero or more operand sets to union.
                       all these must be iterable
        :returns: the union set
        :rtype: :class:`set`

        .. note::

           It sends a :redis:`SUNION` command for other :class:`Set`
           objects.  For other ordinary Python iterables, it unions
           all in the memory.

        """
        online_sets = {self.value_type: [self]}
        offline_sets = []
        for operand in sets:
            if (isinstance(operand, Set) and self.session is operand.session):
                group = online_sets.setdefault(operand.value_type, [])
                group.append(operand)
            else:
                offline_sets.append(operand)
        union = set()
        for value_type, group in online_sets.iteritems():
            keys = (s.key for s in group)
            subset = self.session.client.sunion(*keys)
            decode = value_type.decode
            union.update(decode(member) for member in subset)
        for operand in offline_sets:
            union.update(operand)
        return union

    def intersection(self, *sets):
        """Gets the intersection of the given sets.

        :param \*sets: zero or more operand sets to get intersection.
                       all these must be iterable
        :returns: the intersection
        :rtype: :class:`set`

        """
        online_sets = []
        offline_sets = []
        for operand in sets:
            if (isinstance(operand, Set) and self.session is operand.session):
                if self.value_type != operand.value_type:
                    return set()
                online_sets.append(operand)
            else:
                offline_sets.append(operand)
        keys = frozenset(s.key for s in online_sets)
        if keys:
            inter = self.session.client.sinter(self.key, *keys)
            decode = self.value_type.decode
            online = set(decode(m) for m in inter)
        else:
            online = self
        if offline_sets:
            base = offline_sets[0]
            if not isinstance(base, set):
                base = set(base)
            base.intersection_update(online, *offline_sets[1:])
            return base
        return online if isinstance(online, set) else set(online)

    def add(self, element):
        """Adds an ``element`` to the set.  This has no effect
        if the ``element`` is already present.

        :param element: an element to add

        .. note::

           This method is a direct mapping to :redis:`SADD` comamnd.

        """
        member = self.value_type.encode(element)
        self.session.client.sadd(self.key, member)

    def discard(self, element):
        """Removes an ``element`` from the set if it is a member.
        If the ``element`` is not a member, does nothing.

        :param element: an element to remove

        .. note::

           This method is mapped to :redis:`SREM` command.

        """
        try:
            member = self.value_type.encode(element)
        except TypeError:
            return
        self.session.client.srem(self.key, member)

    def pop(self):
        """Removes an arbitrary element from the set and returns it.
        Raises :exc:`KeyError` if the set is empty.

        :returns: a removed arbitrary element
        :raises: :exc:`KeyError` if the set is empty

        .. note::

           This method is directly mapped to :redis:`SPOP` command.

        """
        popped = self.session.client.spop(self.key)
        if popped is None:
            raise KeyError('pop from an empty set')
        return self.value_type.decode(popped)

    def clear(self):
        """Removes all elements from this set.

        .. note::

           Under the hood it simply :redis:`DEL` the key.

        """
        self.session.client.delete(self.key)

    def update(self, *sets):
        """Updates the set with union of itself and operands.

        :param \*sets: zero or more operand sets to union.
                       all these must be iterable

        .. note::

           It sends a :redis:`SUNIONSTORE` command for other
           :class:`Set` objects and a :redis:`SADD` command for
           other ordinary Python iterables.

           Multiple operands of :redis:`SADD` command was supported
           since Redis 2.4.0, so it would send multiple :redis:`SADD`
           commands if the Redis version is less than 2.4.0.

        """
        online_sets = []
        offline_sets = []
        for operand in sets:
            if isinstance(operand, Set) and self.session is operand.session:
                if self.value_type == operand.value_type:
                    online_sets.append(operand)
                else:
                    raise TypeError(
                        'value_type mismatch; tried union of {0!r} and '
                        '{1!r}'.format(self.value_type, operand.value_type)
                    )
            else:
                offline_sets.append(operand)
        pipe = self.session.client.pipeline()
        if online_sets:
            keys = (operand.key for operand in online_sets)
            pipe.sunionstore(self.key, self.key, *keys)
        update = self._raw_update
        for operand in offline_sets:
            update(operand, pipe)
        pipe.execute()

    def _raw_update(self, members, pipe):
        key = self.key
        encode = self.value_type.encode
        data = (encode(v) for v in members)
        if self.session.server_version_info < (2, 4, 0):
            for member in data:
                pipe.sadd(key, member)
        else:
            pipe.sadd(key, *members)

    def __repr__(self):
        cls = type(self)
        values = list(self)
        values.sort()
        els = ', '.join(repr(v) for v in values)
        return '<{0}.{1} {{{2}}}>'.format(cls.__module__, cls.__name__, els)

