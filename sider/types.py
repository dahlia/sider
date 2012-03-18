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
import numbers


class Bulk(object):
    """The abstract base class to be subclassed.  You have to implement
    :meth:`encode()` and :meth:`decode()` methods in subclasses.

    """

    @classmethod
    def ensure_subtype(cls, subtype, parameter=None):
        """Raises a :exc:`TypeError` if the given ``subtype`` is not
        a subclass of the class.

        .. sourcecode:: pycon

           >>> Integer.ensure_subtype(Bulk)  # doctest: +NORMALIZE_WHITESPACE
           Traceback (most recent call last):
             ...
           TypeError: expected a subtype of sider.types.Integer,
                      but sider.types.Bulk was passed
           >>> Bulk.ensure_subtype(1)  # doctest: +NORMALIZE_WHITESPACE
           Traceback (most recent call last):
             ...
           TypeError: expected a type, not 1

        Otherwise it simply does nothing.

        .. sourcecode:: pycon

           >>> Bulk.ensure_subtype(Bulk)
           >>> Bulk.ensure_subtype(ByteString)
           >>> ByteString.ensure_subtype(ByteString)

        If an optional ``parameter`` name has present, the error message
        becomes better.

        .. sourcecode:: pycon

           >>> Integer.ensure_subtype(Bulk,
           ...   parameter='argname')  # doctest: +NORMALIZE_WHITESPACE
           Traceback (most recent call last):
             ...
           TypeError: argname must be a subtype of sider.types.Integer,
                      but sider.types.Bulk was passed
           >>> Bulk.ensure_subtype(1,
           ...   parameter='argname')  # doctest: +NORMALIZE_WHITESPACE
           Traceback (most recent call last):
             ...
           TypeError: argname must be a type, not 1

        :param subtype: a type expected to be a subtype of the class
        :type subtype: :class:`type`
        :param parameter: an optional parameter name.
                          if present the error message becomes better
        :type parameter: :class:`str`
        :raises: :exc:`~exceptions.TypeError` if the given ``subtype``
                 is not a subclass of the class

        """
        if not isinstance(subtype, type):
            if parameter:
                msg = '{0} must be a type, not {1!r}'
            else:
                msg = 'expected a type, not {1!r}'
            raise TypeError(msg.format(parameter, subtype))
        elif not issubclass(subtype, cls):
            if parameter:
                msg = '{0} must be a subtype of {1}, but {2} was passed'
            else:
                msg = 'expected a subtype of {1}, but {2} was passed'
            typename = '.'.join((cls.__module__, cls.__name__))
            subname = '.'.join((subtype.__module__, subtype.__name__))
            raise TypeError(msg.format(parameter, typename, subname))

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
            raise ValueError('expected a byte str, not ' + repr(value))
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
            raise ValueError('expected a unicode string, not ' + repr(value))
        return value.encode('utf-8')

    def decode(self, bulk):
        return bulk.decode('utf-8')

