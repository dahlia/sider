Custom types
============

.. seealso::

   Module :mod:`sider.types`
      Conversion between Python and Redis types.

.. todo::

   Dealing with mutable objects.


When built-in types aren't enough for you
-----------------------------------------

Sometimes there could be desires to deal with your own Python objects.
For example, how can we store objects of these types into Redis using Sider?::

    class Point(object):
        """Geometric 2D (left, top) point."""

        def __init__(self, left, top):
            self.left = left
            self.top = top

        def __add__(self, size):
            return Point(self.left + size.width, self.top + size.height)

        def __sub__(self, size):
            return Point(self.left - size.width, self.top - size.height)

        def __repr__(self):
            return 'Point({0!1}, {1!r})'.format(self.left, self.top)


    class Size(object):
        """Geometric 2D (width, height) size."""

        def __init__(self, width, height):
            self.width = width
            self.height = height

        def __add__(self, point):
            return Point(point.left + self.width, point.top + self.height)

        def __sub__(self, size):
            return Point(point.left - self.width, point.top - self.height)

        def __repr__(self):
            return 'Size({0!1}, {1!r})'.format(self.width, self.height)

This guide will explain how to build custom types.


Extending :class:`~sider.types.Tuple` type
------------------------------------------

The easiest way to build a custom type is subtyping :class:`sider.types.Tuple`.
Basically it is for storing :class:`tuple` values as its name shows.

>>> from sider.types import Integer, Tuple
>>> point_tuple_type = Tuple(Integer, Integer)
>>> encoded = point_tuple_type.encode((10, 20))
>>> point_tuple_type.decode(encoded)
(10, 20)

By extending this you can build your own custom type.  What you have to
override is just three methods: :meth:`~sider.types.Tuple.__init__()`,
:meth:`~sider.types.Tuple.encode()`, :meth:`~side.types.Tuple.decode()`.

:class:`~sider.types.Tuple`'s initializer takes types of its values.
What you have to do in the method is to simply fix these types:
in the example, members of objects to store are width and height, two integers.

:class:`~sider.types.Tuple.encode()` method takes an object to encode and
returns an encoded byte string.

:class:`~sider.types.Tuple.decode()` method takes a byte string to decode and
returns a decoded Python object (in the example, point object).

The following code is defining a new custom type for storing point values::

    from sider.types import Integer, Tuple


    class PointType(Tuple):
        """Sider type for storing :class:`Point` objects.  Internally
        it stores values as tuples like (left, top).

        """

        def __init__(self):
            super(PointType, self).__init__(Integer, Integer)

        def encode(self, value):
            if not isinstance(value, Point):
                raise TypeError('expected a Point instance, not ' + repr(value))
            return super(PointType, self).encode((value.left, value.top))

        def decode(self, bulk):
            xy = super(PointType, self).decode(bulk)
            return Point(*xy)

It will work for you very well.

>>> point_type = PointType()
>>> encoded = point_type.encode(Point(10, 20))
>>> point_type.decode(encoded)
Point(10, 20)


Extending :class:`~sider.types.Bulk` type
-----------------------------------------

Sometimes you may want to control the encoded representation of your objects
in Redis.  For example, bulks (byte strings) encoded using
:class:`~sider.types.Tuple` aren't readable.  In that case, you can encode
your objects to and decode from byte string representation you want,
by subclassing :class:`sider.types.Bulk` type.

For example, you may want to encode size values into byte strings like
``'%(width)d*%(height)d'``. ::

    import re
    from sider.types import Bulk


    class SizeType(Bulk):
        """Sider type for storing :class:`Size` objects.  Internally
        it stores values as bytes like ``'%(width)d*%(height)d'``.

        """

        FORMAT = '{0}*{1}'
        PATTERN = re.compile(r'^(\d+)\*(\d+)$')

        def encode(self, value):
            if not isinstance(value, Size):
                raise TypeError('expected a Size instance, not ' + repr(value))
            encoded = self.FORMAT.format(value.width, value.height)
            return super(SizeType, self).encode(encoded)

        def decode(self, bulk):
            encoded = super(SizeType, self).encode(bulk)
            match = self.PATTERN.match(encoded)
            if not match:
                raise ValueError('invalid bulk: '+ repr(encoded))
            return Size(int(match.group(1)), int(match.group(2)))

It works like:

>>> size_type = SizeType()
>>> size_type.encode(Size(12, 34))
'12*34'
>>> size_type.decode(_)
Size(12, 34)

