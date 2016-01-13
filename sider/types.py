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

.. todo::

   - :class:`Complex` that takes :class:`complex`.
   - :class:`Real` that takes real numbers (:class:`numbers.Real`).

   Anything more?

"""
from __future__ import absolute_import
import sys
import re
import collections
import numbers
import datetime
import uuid
from .lazyimport import list, set, sortedset
from .datetime import UTC, FixedOffset


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
        :raises exceptions.TypeError:
           if the given ``subtype`` is not a subclass of the class

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
        :exc:`~exceptions.NotImplementedError`.

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
        :exc:`~exceptions.NotImplementedError`.

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


class Hash(Value):
    """The type object for :class:`sider.hash.Hash` objects and other
    :class:`collections.Mapping` objects.

    :param key_type: the type of keys the hash will contain.
                     default is :class:`String`
    :type key_type: :class:`Bulk`, :class:`type`
    :param value_type: the type of values the hash will contain.
                       default is :class:`String`
    :type value_type: :class:`Bulk`, :class:`type`

    """

    def __init__(self, key_type=None, value_type=None):
        if key_type is None:
            key_type = String()
        else:
            key_type = Bulk.ensure_value_type(key_type, parameter='key_type')
        if value_type is None:
            value_type = String()
        else:
            value_type = Bulk.ensure_value_type(value_type,
                                                parameter='value_type')
        self.key_type = key_type
        self.value_type = value_type

    def load_value(self, session, key):
        from .hash import Hash
        return Hash(session, key,
                    key_type=self.key_type, value_type=self.value_type)

    def save_value(self, session, key, value):
        if not isinstance(value, collections.Mapping):
            raise TypeError('expected a mapping object, not ' + repr(value))
        from .hash import Hash
        obj = Hash(session, key,
                   key_type=self.key_type, value_type=self.value_type)
        if value:
            pipe = session.client.pipeline()
            pipe.delete(key)
            obj._raw_update(value, pipe)
            pipe.execute()
        else:
            session.client.delete(key)
        return obj


class List(Value):
    """The type object for :class:`sider.list.List` objects and other
    :class:`collections.Sequence` objects except strings.
    (Use :class:`ByteString` or :class:`UnicodeString` for strings.)

    :param value_type: the type of values the list will contain.
                       default is :class:`String`
    :type value_type: :class:`Bulk`, :class:`type`

    """

    def __init__(self, value_type=None):
        if value_type is None:
            self.value_type = String()
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
                       default is :class:`String`
    :type value_type: :class:`Bulk`, :class:`type`

    """

    def __init__(self, value_type=None):
        if value_type is None:
            self.value_type = String()
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


class SortedSet(Set):
    """The type object for :class:`sider.sortedset.SortedSet` objects.

    :param value_type: the type of values the sorted set will contain.
                       default is :class:`String`
    :type value_type: :class:`Bulk`, :class:`type`

    """

    def load_value(self, session, key):
        return sortedset.SortedSet(session, key, value_type=self.value_type)

    def save_value(self, session, key, value):
        if not isinstance(value, (collections.Set, collections.Mapping)):
            raise TypeError('expected a set-like or mapping object, not ' +
                            repr(value))
        obj = sortedset.SortedSet(session, key, value_type=self.value_type)
        encode = self.value_type.encode
        if session.server_version_info < (2, 4, 0):
            if isinstance(value, collections.Mapping):
                pairs = [
                    (encode(el), score)
                    for el, score in getattr(value, 'iteritems', value.items)()
                ]
            else:
                pairs = [(encode(el), 1) for el in value]
            def block(trial, transaction):
                obj.clear()
                zadd = session.client.zadd
                for el, score in pairs:
                    zadd(key, score, el)
        else:
            if isinstance(value, collections.Mapping):
                items = getattr(value, 'iteritems', value.items)
                def args():
                    for el, score in items():
                        yield score
                        yield encode(el)
            else:
                def args():
                    for el in value:
                        yield 1
                        yield encode(el)
            args = tuple(args())
            def block(trial, transaction):
                obj.clear()
                if args:
                    session.client.zadd(key, *args)
        session.transaction(block, [key], ignore_double=True)
        return obj


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
        :raises exceptions.TypeError:
           if the type of a given value is not acceptable by this type

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


class Tuple(Bulk):
    r"""Stores tuples of fixed fields.  It can be used for
    compositing multiple fields into one field in ad-hoc way.
    For example, if you want to store 3D point value without
    defining new :class:`Type`::

        Tuple(Integer, Integer, Integer)

    The above type will store three integers in a field.

    .. sourcecode:: pycon

       >>> int_str_int = Tuple(Integer, ByteString, Integer)
       >>> int_str_int.encode((123, 'abc\ndef', 456))
       '3,7,3\n123\nabc\ndef\n456'
       >>> int_str_int.decode(_)
       (123, 'abc\ndef', 456)

    Encoded values become a bulk bytes.  It consists of a header
    line and other lines that contain field values.  The first
    header line is a comma-separated integers that represent
    each byte size of encoded field values.

    .. productionlist::
       tuple: `header` (newline field)*
       header: [`size` ("," `size`)*]
       size: digit+
       digit: "0" | "1" | "2" | "3" | "4" |
            : "5" | "6" | "7" | "8" | "9"

    :param \*field_types: the variable number of field types

    """

    #: (:class:`tuple`) The tuple of field types.
    field_types = None

    def __init__(self, *field_types):
        self.field_types = tuple(Bulk.ensure_value_type(t)
                                 for t in field_types)

    def encode(self, value):
        if not isinstance(value, tuple):
            raise TypeError('expected a tuple, not ' + repr(value))
        fields_num = len(self.field_types)
        tuple_len = len(value)
        if fields_num < tuple_len:
            raise ValueError('too many values to unpack: ' + repr(value))
        elif fields_num > tuple_len:
            if fields_num > 1:
                msg = 'need {0} values to unpack: {1!r}'
            else:
                msg = 'need {0} value to unpack: {1!r}'
            raise ValueError(msg.format(fields_num, value))
        codes = [field.encode(val)
                 for field, val in zip(self.field_types, value)]
        codes.insert(0, b','.join(str(len(code)).encode('ascii')
                                 for code in codes))
        return b'\n'.join(codes)

    def decode(self, bulk):
        pos = bulk.index(b'\n')
        header = bulk[:pos]
        sizes = map(int, header.split(b','))
        pos += 1
        values = []
        for field, size in zip(self.field_types, sizes):
            code = bulk[pos:pos + size]
            value = field.decode(code)
            values.append(value)
            pos += size + 1
        return tuple(values)


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
        return str(value).encode('ascii')

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

    try:
        bytes_type = bytes
    except NameError:
        bytes_type = str

    def encode(self, value):
        if not isinstance(value, self.bytes_type):
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

    try:
        string_type = unicode
    except NameError:
        string_type = str

    def encode(self, value):
        if not isinstance(value, self.string_type):
            raise TypeError('expected a unicode string, not ' + repr(value))
        return value.encode('utf-8')

    def decode(self, bulk):
        return bulk.decode('utf-8')


if sys.version_info[0] == 3:  # python 3.x
    String = UnicodeString
else:
    String = ByteString


class Boolean(Integer):
    """Stores :class:`bool` values as ``'1'`` or ``'0'``.

    .. sourcecode:: pycon

       >>> boolean = Boolean()
       >>> boolean.encode(True)
       '1'
       >>> boolean.encode(False)
       '0'

    """

    def encode(self, value):
        return super(Boolean, self).encode(1 if value else 0)

    def decode(self, bulk):
        return bool(super(Boolean, self).decode(bulk))


class Date(Bulk):
    """Stores :class:`datetime.date` values.  Dates are internally
    formatted in :rfc:`3339` format e.g. ``2012-03-28``.

    .. sourcecode:: pycon

       >>> import datetime
       >>> date = Date()
       >>> date.encode(datetime.date(2012, 3, 28))
       '2012-03-28'
       >>> date.decode(_)
       datetime.date(2012, 3, 28)

    """

    #: The :mod:`re` pattern that matches to :rfc:`3339` formatted date
    #: string e.g. ``'2012-03-28'``.
    DATE_PATTERN = re.compile(
        br'^(?P<year>\d{4})-(?P<month>\d\d)-(?P<day>\d\d)$'
    )

    #: (:class:`str`) The :meth:`~datetime.date.strftime()` format string
    #: for :rfc:`3339`.
    DATE_FORMAT = '%Y-%m-%d'

    def encode(self, value):
        if not isinstance(value, datetime.date):
            raise TypeError('expected a datetime.date, not ' + repr(value))
        return value.strftime(self.DATE_FORMAT).encode('ascii')

    def decode(self, bulk):
        match = self.DATE_PATTERN.search(bulk)
        if match:
            year = int(match.group('year'))
            month = int(match.group('month'))
            day = int(match.group('day'))
            return datetime.date(year, month, day)
        fmt = self.DATE_FORMAT
        msg = 'expected a {0!r} format, not {1!r}'.format(fmt, bulk)
        raise ValueError(msg)


class DateTime(Bulk):
    """Stores naive :class:`datetime.datetime` values.
    Values are internally formatted in :rfc:`3339` format
    e.g. ``2012-03-28T09:21:34.638972``.

    .. sourcecode:: pycon

       >>> dt = DateTime()
       >>> dt.decode('2012-03-28T09:21:34.638972')
       datetime.datetime(2012, 3, 28, 9, 21, 34, 638972)
       >>> dt.encode(_)
       '2012-03-28T09:21:34.638972'

    It doesn't store :attr:`~datetime.datetime.tzinfo` data.

    .. sourcecode:: pycon

       >>> from sider.datetime import UTC
       >>> decoded = dt.decode('2012-03-28T09:21:34.638972Z')
       >>> decoded
       datetime.datetime(2012, 3, 28, 9, 21, 34, 638972)
       >>> dt.encode(decoded.replace(tzinfo=UTC))
       '2012-03-28T09:21:34.638972'

    .. note::

       If you must be aware of time zone, use :class:`TZDateTime`
       instead.

    """

    DATETIME_PATTERN = re.compile(
        br'^(?P<year>\d{4})-(?P<month>\d\d)-(?P<day>\d\d)T(?P<hour>\d\d):'
        br'(?P<minute>\d\d):(?P<second>\d\d)(?:\.(?P<microsecond>\d{6}))?'
        br'(?P<tz>(?P<tz_utc>Z)|(?P<tz_offset_sign>[+-])(?P<tz_offset_hour>'
        br'\d\d):(?P<tz_offset_minute>\d\d))?$'
    )

    def encode(self, value):
        if not isinstance(value, datetime.datetime):
            raise TypeError('expected a datetime.datetime, not ' + repr(value))
        if value.tzinfo is not None:
            value = value.replace(tzinfo=None)
        return value.isoformat().encode('ascii')

    def decode(self, bulk):
        parsed = self.parse_datetime(bulk)
        if parsed.tzinfo:
            return parsed.replace(tzinfo=None)
        return parsed

    def parse_datetime(self, bulk):
        r"""Parses a :rfc:`3339` formatted string into
        :class:`datetime.datetime`.

        .. sourcecode:: pycon

           >>> dt = DateTime()
           >>> dt.parse_datetime('2012-03-28T09:21:34.638972')
           datetime.datetime(2012, 3, 28, 9, 21, 34, 638972)

        Unlike :meth:`decode()` it is aware of
        :attr:`~datetime.datetime.tzinfo` data if the string contains
        time zone notation.

        .. sourcecode:: pycon

           >>> a = dt.parse_datetime('2012-03-28T09:21:34.638972Z')
           >>> a  # doctest: +NORMALIZE_WHITESPACE
           datetime.datetime(2012, 3, 28, 9, 21, 34, 638972,
                             tzinfo=sider.datetime.Utc())
           >>> b = dt.parse_datetime('2012-03-28T18:21:34.638972+09:00')
           >>> b  # doctest: +NORMALIZE_WHITESPACE
           datetime.datetime(2012, 3, 28, 18, 21, 34, 638972,
                             tzinfo=sider.datetime.FixedOffset(540))
           >>> a == b
           True

        :param bulk: a :rfc:`3339` formatted string
        :type bulk: :class:`basestring`
        :returns: a parsing result
        :rtype: :class:`datetime.datetime`

        .. note::

           It is for internal use and :meth:`decode()` method actually
           uses this method.

        """
        match = self.DATETIME_PATTERN.search(bulk)
        if match:
            year = int(match.group('year'))
            month = int(match.group('month'))
            day = int(match.group('day'))
            hour = int(match.group('hour'))
            minute = int(match.group('minute'))
            second = int(match.group('second'))
            microsecond = int(match.group('microsecond'))
            if match.group('tz'):
                if match.group('tz_utc'):
                    tzinfo = UTC
                else:
                    tzplus = match.group('tz_offset_sign') == '+'
                    tzhour = int(match.group('tz_offset_hour'))
                    tzmin = int(match.group('tz_offset_minute'))
                    tzoffset = datetime.timedelta(hours=tzhour, minutes=tzmin)
                    tzinfo = FixedOffset(tzoffset if tzplus else -tzoffset)
            else:
                tzinfo = None
            return datetime.datetime(year, month, day, hour, minute, second,
                                     microsecond, tzinfo=tzinfo)
        raise ValueError('expected a RFC 3339 compliant datetime.datetime '
                         'string, not ' + repr(bulk))


class TZDateTime(DateTime):
    """Similar to :class:`DateTime` except it accepts only tz-aware
    :class:`datetime.datetime` values.  All values are internally
    stored in :const:`~sider.datetime.UTC`.

    .. sourcecode:: pycon

       >>> from sider.datetime import FixedOffset
       >>> dt = datetime.datetime(2012, 3, 28, 18, 21, 34, 638972,
       ...                        tzinfo=FixedOffset(540))
       >>> tzdt = TZDateTime()
       >>> tzdt.encode(dt)
       '2012-03-28T09:21:34.638972Z'
       >>> tzdt.decode(_)  # doctest: +NORMALIZE_WHITESPACE
       datetime.datetime(2012, 3, 28, 9, 21, 34, 638972,
                         tzinfo=sider.datetime.Utc())

    If any naive :class:`datetime.datetime` has passed it will
    raise :exc:`~exceptions.ValueError`.

    """

    def encode(self, value):
        if not isinstance(value, datetime.datetime):
            raise TypeError('expected a datetime.datetime, not ' + repr(value))
        elif value.tzinfo is None:
            raise ValueError('datetime.datetime must be aware of tzinfo')
        encoded = super(TZDateTime, self).encode(value.astimezone(UTC))
        return encoded + b'Z'

    def decode(self, bulk):
        parsed = self.parse_datetime(bulk)
        if parsed.tzinfo is None:
            raise ValueError('datetime.datetime must be aware of tzinfo')
        return parsed


class Time(Bulk):
    """Stores naive :class:`datetime.time` values.

    .. sourcecode:: pycon

       >>> time = Time()
       >>> time.decode('09:21:34.638972')
       datetime.time(9, 21, 34, 638972)
       >>> time.encode(_)
       '09:21:34.638972'

    It doesn't store :attr:`~datetime.time.tzinfo` data.

    .. sourcecode:: pycon

       >>> from sider.datetime import UTC
       >>> time = Time()
       >>> decoded = time.decode('09:21:34.638972Z')
       >>> decoded
       datetime.time(9, 21, 34, 638972)
       >>> time.encode(decoded.replace(tzinfo=UTC))
       '09:21:34.638972'

    .. note::

       If you must be aware of time zone, use :class:`TZTime`
       instead.

    """

    TIME_PATTERN = re.compile(
        br'^(?P<hour>\d\d):(?P<minute>\d\d):(?P<second>\d\d)'
        br'(?:\.(?P<microsecond>\d{6}))?'
        br'(?P<tz>(?P<tz_utc>Z)|(?P<tz_offset_sign>[+-])(?P<tz_offset_hour>'
        br'\d\d):(?P<tz_offset_minute>\d\d))?$'
    )

    def encode(self, value):
        if not isinstance(value, datetime.time):
            raise TypeError('expected a datetime.time, not ' + repr(value))
        if value.tzinfo is not None:
            value = value.replace(tzinfo=None)
        return value.isoformat().encode('ascii')

    def decode(self, bulk):
        return self.parse_time(bulk, drop_tzinfo=True)

    def parse_time(self, bulk, drop_tzinfo):
        """Parses an encoded :class:`datetime.time`.

        :param bulk: an encoded time
        :type bulk: :class:`basestring`
        :returns: a parsed time
        :rtype: :class:`datetime.time`

        .. note::

           It is for internal use and :meth:`decode()` method actually
           uses this method.

        """
        match = self.TIME_PATTERN.search(bulk)
        if not match:
            raise ValueError('malformed time: ' + repr(bulk))
        hour = int(match.group('hour'))
        minute = int(match.group('minute'))
        second = int(match.group('second'))
        microsecond = match.group('microsecond')
        microsecond = int(microsecond) if microsecond else 0
        if not drop_tzinfo and match.group('tz'):
            if match.group('tz_utc'):
                tzinfo = UTC
            else:
                tzplus = match.group('tz_offset_sign') == '+'
                tzhour = int(match.group('tz_offset_hour'))
                tzmin = int(match.group('tz_offset_minute'))
                tzoffset = datetime.timedelta(hours=tzhour, minutes=tzmin)
                tzinfo = FixedOffset(tzoffset if tzplus else -tzoffset)
        else:
            tzinfo = None
        return datetime.time(hour, minute, second, microsecond, tzinfo=tzinfo)


class TZTime(Time):
    """Similar to :class:`Time` except it accepts only tz-aware
    :class:`datetime.time` values.

    .. sourcecode:: pycon

       >>> from sider.datetime import FixedOffset
       >>> time = datetime.time(18, 21, 34, 638972,
       ...                      tzinfo=FixedOffset(540))
       >>> tztime = TZTime()
       >>> tztime.encode(time)
       '18:21:34.638972+09:00'
       >>> tztime.decode(_)  # doctest: +NORMALIZE_WHITESPACE
       datetime.time(18, 21, 34, 638972,
                     tzinfo=sider.datetime.FixedOffset(540))
       >>> utctime = datetime.time(9, 21, 34, 638972, tzinfo=UTC)
       >>> tztime.encode(utctime)
       '09:21:34.638972Z'
       >>> tztime.decode(_)
       datetime.time(9, 21, 34, 638972, tzinfo=sider.datetime.Utc())

    If any naive :class:`datetime.time` has passed it will
    raise :exc:`~exceptions.ValueError`.

    """

    def encode(self, value):
        if not isinstance(value, datetime.time):
            raise TypeError('expected a datetime.time, not ' + repr(value))
        elif value.tzinfo is None:
            raise ValueError('datetime.time must be aware of tzinfo')
        if value.tzinfo is UTC:
            result = value.replace(tzinfo=None).isoformat() + 'Z'
            return result.encode('ascii')
        return value.isoformat().encode('ascii')

    def decode(self, bulk):
        time = self.parse_time(bulk, drop_tzinfo=False)
        if time.tzinfo is None:
            raise ValueError('datetime.time must be aware of tzinfo')
        return time


class TimeDelta(Bulk):
    """Stores :class:`datetime.timedelta` values.

    .. sourcecode:: pycon

       >>> import datetime
       >>> td = TimeDelta()
       >>> delta = datetime.timedelta(days=3, seconds=53, microseconds=123123)
       >>> td.encode(delta)
       '3,53,123123'
       >>> td.decode(_)
       datetime.timedelta(3, 53, 123123)

    """

    TIMEDELTA_FORMAT = '{0.days},{0.seconds},{0.microseconds}'
    TIMEDELTA_PATTERN = re.compile(br'^(?P<days>\d+),(?P<seconds>\d+),'
                                   br'(?P<microseconds>\d{1,6})$')

    def encode(self, value):
        if not isinstance(value, datetime.timedelta):
            raise TypeError('expected a datetime.timedelta, not ' +
                            repr(value))
        return self.TIMEDELTA_FORMAT.format(value).encode('ascii')

    def decode(self, bulk):
        match = self.TIMEDELTA_PATTERN.search(bulk)
        if match:
            days = int(match.group('days'))
            seconds = int(match.group('seconds'))
            microseconds = int(match.group('microseconds'))
            return datetime.timedelta(days=days,
                                      seconds=seconds,
                                      microseconds=microseconds)
        raise ValueError('invalid bulk: ' + repr(bulk))


class UUID(Bulk):
    """Stores :class:`uuid.UUID` values.  For example:

    .. sourcecode:: pycon

       >>> import uuid
       >>> u = UUID()
       >>> u.encode(uuid.UUID(int=134626331218489933988508161913704617318))
       '65481698-2f85-4bd6-8f7c-ee8aaecf1566'
       >>> u.decode('65481698-2f85-4bd6-8f7c-ee8aaecf1566')
       UUID('65481698-2f85-4bd6-8f7c-ee8aaecf1566')

    """
    def encode(self, value):
        if not isinstance(value, uuid.UUID):
            raise TypeError('expected an uuid.UUID, not ' + repr(value))
        return str(value).encode('ascii')

    def decode(self, bulk):
        return uuid.UUID(bulk.decode('ascii'))
