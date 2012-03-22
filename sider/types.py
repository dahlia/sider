""":mod:`sider.types` --- Conversion between Python and Redis types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In Redis all data are byte strings --- *bulks*.  Lists are lists of byte
strings, sets are sets of byte strings, and hashes consist of byte string
keys and byte string values.

To store richier objects into Redis we have to encode Python values and
decode Redis data.  :class:`Bulk` and its subclasses are for that, it
defines two basic methods: :meth:`~Bulk.encode()` and
:meth:`~Bulk.decode()`.  For example, :class:`Integer` encodes Python
:class:`int` ``3`` into Redis bulk ``"3"`` and decodes Redis bulk ``"3"``
into Python :class:`int` ``3``.

"""
from __future__ import absolute_import
import collections
import numbers
from .lazyimport import list, set


class Value(object):
    """There are two layers behind Sider types: the lower one is
    this :class:`Value` and the higher one is :class:`Bulk`.

    :class:`Value` types can be set to Redis keys, but unlike
    :class:`Bulk` it cannot be a value type of other rich
    :class:`Value` types e.g. :class:`List`, :class:`Hash`.

    In most cases you (users) don't have to subclass :class:`Value`,
    and should not.  Direct subclasses of :class:`Value` aren't about
    encodings/decodings of Python object but simply Python-side
    representations of `Redis types`__.  It actually doesn't have
    methods like :meth:`~Bulk.encode()` and :meth:`~Bulk.decode()`.
    These methods appear under :class:`Bulk` or its subtypes.

    But it's about how to save Python objects into Redis keys and
    how to load values from associated Redis keys.  There are several
    commands to save like :redis:`SET`, :redis:`MSET`, :redis:`HSET`,
    :redis:`RPUSH` and the rest in Redis and subtypes have to decide
    which command of those to use.

    All subtypes of :class:`Value` implement :meth:`save_value()`
    and :meth:`load_value()` methods.  The constructor which takes
    no arguments have to be implemented as well.

    __ http://redis.io/topics/data-types

    """

    @classmethod
    def ensure_value_type(cls, value_type, parameter=None):
        """Raises a :exc:`TypeError` if the given ``value_type`` is not
        an instance of nor a subclass of the class.

        .. sourcecode:: pycon

           >>> Integer.ensure_value_type(Bulk
           ... )  # doctest: +NORMALIZE_WHITESPACE
           Traceback (most recent call last):
             ...
           TypeError: expected a subtype of sider.types.Integer,
                      but sider.types.Bulk was passed
           >>> Integer.ensure_value_type(UnicodeString()
           ... )  # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
           Traceback (most recent call last):
             ...
           TypeError: expected an instance of sider.types.Integer,
                      but <sider.types.UnicodeString object at ...>
                      was passed
           >>> Bulk.ensure_value_type(1)
           Traceback (most recent call last):
             ...
           TypeError: expected a type, not 1

        Otherwise it simply returns an instance of
        the given ``value_type``.

        .. sourcecode:: pycon

           >>> Bulk.ensure_value_type(Bulk)  # doctest: +ELLIPSIS
           <sider.types.Bulk object at ...>
           >>> Bulk.ensure_value_type(ByteString)  # doctest: +ELLIPSIS
           <sider.types.ByteString object at ...>
           >>> ByteString.ensure_value_type(ByteString
           ... )  # doctest: +ELLIPSIS
           <sider.types.ByteString object at ...>
           >>> bytestr = ByteString()
           >>> ByteString.ensure_value_type(bytestr) # doctest: +ELLIPSIS
           <sider.types.ByteString object at ...>

        If an optional ``parameter`` name has present, the error message
        becomes better.

        .. sourcecode:: pycon

           >>> Integer.ensure_value_type(Bulk,
           ...   parameter='argname')  # doctest: +NORMALIZE_WHITESPACE
           Traceback (most recent call last):
             ...
           TypeError: argname must be a subtype of sider.types.Integer,
                      but sider.types.Bulk was passed
           >>> Integer.ensure_value_type(UnicodeString(),
           ...   parameter='argname'
           ... )  # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
           Traceback (most recent call last):
             ...
           TypeError: argname must be an instance of sider.types.Integer,
                      but <sider.types.UnicodeString object at ...>
                      was passed
           >>> Bulk.ensure_value_type(1, parameter='argname')
           Traceback (most recent call last):
             ...
           TypeError: argname must be a type, not 1

        :param value_type: a type expected to be a subtype of the class
        :type value_type: :class:`Value`, :class:`type`
        :param parameter: an optional parameter name.
                          if present the error message becomes better
        :type parameter: :class:`str`
        :raises: :exc:`~exceptions.TypeError` if the given ``subtype``
                 is not a subclass of the class

        """
        typename = '.'.join((cls.__module__, cls.__name__))
        if isinstance(value_type, type):
            subname = '.'.join((value_type.__module__, value_type.__name__))
            if issubclass(value_type, cls):
                try:
                    return value_type()
                except TypeError as e:
                    raise TypeError(
                        '{0} must implement the constructor which takes '
                        'no arguments; {1}'.format(subname, e)
                    )
            else:
                if parameter:
                    msg = '{0} must be a subtype of {1}, but {2} was passed'
                else:
                    msg = 'expected a subtype of {1}, but {2} was passed'
                raise TypeError(msg.format(parameter, typename, subname))
        elif isinstance(value_type, Value):
            if isinstance(value_type, cls):
                return value_type
            else:
                if parameter:
                    msg = '{0} must be an instance of {1}, ' \
                          'but {2!r} was passed'
                else:
                    msg = 'expected an instance of {1}, but {2!r} was passed'
                raise TypeError(msg.format(parameter, typename, value_type))
        else:
            if parameter:
                msg = '{0} must be a type, not {1!r}'
            else:
                msg = 'expected a type, not {1!r}'
            raise TypeError(msg.format(parameter, value_type))

    def load_value(self, session, key):
        """How to load the value from the given Redis ``key``.
        Subclasses have to implement it.  By default it raises
        :exc:`NotImplementedError`.

        :param session: the session object that stores the given ``key``
        :type session: :class:`sider.session.Session`
        :param key: the key name to load
        :type key: :class:`str`
        :returns: the Python representation of the loaded value

        """
        cls = type(self)
        raise NotImplementedError(
            '{0}.{1}.load_value() method must be '
            'implemented'.format(cls.__module__, cls.__name__)
        )

    def save_value(self, session, key, value):
        """How to save the given ``value`` into the given Redis ``key``.
        Subclasses have to implement it.  By default it raises
        :exc:`NotImplementedError`.

        :param session: the session object going to store
                        the given ``key``--``value`` pair
        :type session: :class:`sider.session.Session`
        :param key: the key name to save the ``value``
        :type key: :class:`str`
        :param value: the value to save into the ``key``
        :returns: the Python representation of the saved value.
                  it is equivalent to the given ``value`` but
                  may not equal nor the same to

        """
        cls = type(self)
        raise NotImplementedError(
            '{0}.{1}.save_value() method must be '
            'implemented'.format(cls.__module__, cls.__name__)
        )

    def __hash__(self):
        return hash(type(self))

    def __eq__(self, operand):
        return type(self) is type(operand)

    def __ne__(self, operand):
        return not (self == operand)


class List(Value):
    """The type object for :class:`sider.list.List` objects and other
    :class:`collections.Sequence` objects except strings.
    (Use :class:`ByteString` or :class:`UnicodeString` for strings.)

    :param value_type: the type of values the list will contain.
                       default is :class:`ByteString`
    :type value_type: :class:`Bulk`, :class:`type`

    """

    def __init__(self, value_type=None):
        if value_type is None:
            self.value_type = ByteString()
        else:
            self.value_type = Bulk.ensure_value_type(value_type,
                                                     parameter='value_type')

    def load_value(self, session, key):
        return list.List(session, key, value_type=self.value_type)

    def save_value(self, session, key, value):
        if not isinstance(value, collections.Sequence):
            raise TypeError('expected a list-like sequence, not ' +
                            repr(value))
        obj = list.List(session, key, value_type=self.value_type)
        pipe = session.client.pipeline()
        pipe.delete(key)
        obj._raw_extend(value, pipe)
        pipe.execute()
        return obj

    def __hash__(self):
        return super(List, self).__hash__() * hash(self.value_type)

    def __eq__(self, operand):
        if super(List, self).__eq__(operand):
            return self.value_type == operand.value_type
        return False


class Set(Value):
    """The type object for :class:`sider.set.Set` objects and other
    :class:`collections.Set` objects.

    :param value_type: the type of values the set will contain.
                       default is :class:`ByteString`
    :type value_type: :class:`Bulk`, :class:`type`

    """

    def __init__(self, value_type=None):
        if value_type is None:
            self.value_type = ByteString()
        else:
            self.value_type = Bulk.ensure_value_type(value_type,
                                                     parameter='value_type')

    def load_value(self, session, key):
        return set.Set(session, key, value_type=self.value_type)

    def save_value(self, session, key, value):
        if not isinstance(value, collections.Set):
            raise TypeError('expected a set-like object, not ' +
                            repr(value))
        obj = set.Set(session, key, value_type=self.value_type)
        pipe = session.client.pipeline()
        pipe.delete(key)
        obj._raw_update(value, pipe)
        pipe.execute()
        return obj

    def __hash__(self):
        return super(Set, self).__hash__() * hash(self.value_type)

    def __eq__(self, operand):
        if super(Set, self).__eq__(operand):
            return self.value_type == operand.value_type
        return False


class Bulk(Value):
    """The abstract base class to be subclassed.  You have to implement
    :meth:`encode()` and :meth:`decode()` methods in subclasses.

    """

    def encode(self, value):
        """Encodes a Python ``value`` into Redis bulk.  Every subclass of
        :class:`Bulk` must implement this method.  By default it raises
        :exc:`NotImplementedError`.

        :param value: a Python value to encode into Redis bulk
        :returns: an encoded Redis bulk
        :rtype: :class:`str`
        :raises: :exc:`~exceptions.TypeError` if the type of a given
                 value is not acceptable by this type

        """
        cls = type(self)
        raise NotImplementedError(
            '{0}.{1}.encode() method must be '
            'implemented'.format(cls.__module__, cls.__name__)
        )

    def decode(self, bulk):
        """Decodes a Redis ``bulk`` to Python object.  Every subclass of
        :class:`Bulk` must implement this method.  By default it raises
        :exc:`NotImplementedError`.

        :param bulk: a Redis bullk to decode into Python object
        :type bulk: :class:`str`
        :returns: a decoded Python object

        """
        cls = type(self)
        raise NotImplementedError(
            '{0}.{1}.decode() method must be '
            'implemented'.format(cls.__module__, cls.__name__)
        )

    def load_value(self, session, key):
        bulk = session.client.get(key)
        return self.decode(bulk)

    def save_value(self, session, key, value):
        bulk = self.encode(value)
        session.client.set(key, bulk)
        return value


class Integer(Bulk):
    """Stores integers as decimal strings.  For example:
    
    .. sourcecode:: pycon

       >>> integer = Integer()
       >>> integer.encode(42)
       '42'
       >>> integer.decode('42')
       42

    Why it doesn't store integers as binaries but decimals is that
    Redis provides :redis:`INCR`, :redis:`INCRBY`, :redis:`DECR` and
    :redis:`DECRBY` for decimal strings.  You can simply add and
    subtract integers.

    """

    def encode(self, value):
        if not isinstance(value, numbers.Integral):
            raise TypeError('expected an integer, not ' + repr(value))
        return str(value)

    def decode(self, bulk):
        return int(bulk)


class ByteString(Bulk):
    """Stores byte strings.  It stores the given byte strings as these are.
    It works simply transparently for :class:`str` values.

    .. sourcecode:: pycon

       >>> bytestr = ByteString()
       >>> bytestr.encode('annyeong')
       'annyeong'
       >>> bytestr.decode('sayonara')
       'sayonara'

    """

    def encode(self, value):
        if not isinstance(value, str):
            raise TypeError('expected a byte str, not ' + repr(value))
        return value

    def decode(self, bulk):
        return bulk


class UnicodeString(Bulk):
    r"""Stores Unicode strings (:class:`unicode`), not byte strings
    (:class:`str`).  Internally all Unicode strings are encoded into
    and decoded from UTF-8 byte strings.

    .. sourcecode:: pycon

       >>> unistr = UnicodeString()
       >>> unistr.encode(u'\uc720\ub2c8\ucf54\ub4dc')
       '\xec\x9c\xa0\xeb\x8b\x88\xec\xbd\x94\xeb\x93\x9c'
       >>> unistr.decode(_)
       u'\uc720\ub2c8\ucf54\ub4dc'

    """

    def encode(self, value):
        if not isinstance(value, unicode):
            raise TypeError('expected a unicode string, not ' + repr(value))
        return value.encode('utf-8')

    def decode(self, bulk):
        return bulk.decode('utf-8')

