""":mod:`sider.datetime` --- Date and time related utilities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For minimum support of time zones, without adding any external dependencies
e.g. pytz_, Sider had to implement :class:`Utc` class which is a subtype of
:class:`datetime.tzinfo`.

Because :mod:`datetime` module provided by the Python standard library
doesn't contain UTC or any other :class:`~datetime.tzinfo` subtype
implementations.  (A funny thing is that the documentation of :mod:`datetime`
module shows an example of how to implement UTC :class:`~datetime.tzinfo`.)

If you want more various time zones support use the third-party pytz_
package.

.. _UTC: http://en.wikipedia.org/wiki/Coordinated_Universal_Time
.. _pytz: http://pytz.sourceforge.net/

"""
from __future__ import absolute_import, division
import datetime
import numbers


#: (:class:`datetime.timedelta`) No difference.
ZERO_DELTA = datetime.timedelta(0)


class Utc(datetime.tzinfo):
    """The :class:`datetime.tzinfo` implementation of UTC_.

    .. sourcecode:: pycon

       >>> from datetime import datetime
       >>> utc = Utc()
       >>> dt = datetime(2012, 3, 15, 0, 15, 30, tzinfo=utc)
       >>> dt
       datetime.datetime(2012, 3, 15, 0, 15, 30, tzinfo=sider.datetime.Utc())
       >>> utc.utcoffset(dt)
       datetime.timedelta(0)
       >>> utc.dst(dt)
       datetime.timedelta(0)
       >>> utc.tzname(dt)
       'UTC'

    """

    def __new__(cls):
        global UTC
        try:
            return UTC
        except NameError:
            return super(Utc, cls).__new__(cls)

    def utcoffset(self, datetime):
        return ZERO_DELTA

    def dst(self, datetime):
        return ZERO_DELTA

    def tzname(self, datetime):
        return 'UTC'

    def __repr__(self):
        cls = type(self)
        return '{0}.{1}()'.format(cls.__module__, cls.__name__)


#: (:class:`Utc`) The singleton instance of :class:`Utc`.
UTC = Utc()


def utcnow():
    """The current time in :const:`UTC`.  The Python standard library
    also provides :meth:`datetime.datetime.utcnow()` function except
    it returns a naive :class:`datetime.datetime` value.  This function
    returns tz-aware :class:`datetime.datetime` value instead.

    .. sourcecode:: pycon

       >>> import datetime
       >>> datetime.datetime.utcnow()  # doctest: +ELLIPSIS
       datetime.datetime(...)
       >>> utcnow()  # doctest: +ELLIPSIS
       datetime.datetime(..., tzinfo=sider.datetime.Utc())

    :returns: the tz-aware :class:`~datetime.datetime` value
              of the current time
    :rtype: :class:`datetime.datetime`

    """
    return datetime.datetime.utcnow().replace(tzinfo=UTC)


class FixedOffset(datetime.tzinfo):
    """Fixed offset in minutes east from :const:`UTC`.

    .. sourcecode:: pycon

       >>> import datetime
       >>> day = FixedOffset(datetime.timedelta(days=1))
       >>> day
       sider.datetime.FixedOffset(1440)
       >>> day.tzname(None)
       '+24:00'
       >>> half = FixedOffset(-720)
       >>> half
       sider.datetime.FixedOffset(-720)
       >>> half.tzname(None)
       '-12:00'
       >>> half.utcoffset(None)
       datetime.timedelta(-1, 43200)
       >>> zero = FixedOffset(0)
       >>> zero.tzname(None)
       'UTC'
       >>> zero.utcoffset(None)
       datetime.timedelta(0)

    :param offset: the offset integer in minutes,
                   or :class:`~datetime.timedelta` (from a minute to a day)
    :type offset: :class:`numbers.Integral`, :class:`datetime.timedelta`
    :param name: an optional name.  if not present, automatically generated
    :type name: :class:`basestring`
    :raises exceptions.ValueError: when ``offset``'s precision is too short
                                   or too long

    """

    #: (:class:`datetime.timedelta`) The maximum precision of
    #: :meth:`utcoffset()`.
    MAX_PRECISION = datetime.timedelta(days=1)

    #: (:class:`datetime.timedelta`) The minimum precision of
    #: :meth:`utcoffset()`.
    MIN_PRECISION = datetime.timedelta(minutes=1)

    def __init__(self, offset, name=None):
        if isinstance(offset, numbers.Integral):
            offset = datetime.timedelta(minutes=offset)
        elif not isinstance(offset, datetime.timedelta):
            raise TypeError('offset must be an integer or datetime.timedelta')
        if offset < self.MIN_PRECISION and total_seconds(offset) > 0:
            raise ValueError('the minimum precision of offset is minute')
        elif offset > self.MAX_PRECISION:
            raise ValueError('the maximum precision of offset is hour')
        if name is None:
            seconds = int(total_seconds(offset))
            if seconds != 0:
                name = '{0:+03d}:{1:02d}'.format(seconds // 3600,
                                                 abs(seconds) % 3600 // 60)
            else:
                name = 'UTC'
        elif not isinstance(name, basestring):
            raise TypeError('name must be a string, not ' + repr(name))
        self.offset = offset
        self.name = name

    def utcoffset(self, datetime):
        return self.offset

    def tzname(self, datetime):
        return self.name

    def dst(self):
        return ZERO_DELTA

    def __repr__(self):
        cls = type(self)
        min = int(total_seconds(self.offset) / 60)
        return '{0}.{1}({2!r})'.format(cls.__module__, cls.__name__, min)


def total_seconds(timedelta):
    """For Python 2.6 compatibility.  Equivalent to
    :meth:`timedelta.total_seconds() <datetime.timedelta.total_seconds>`
    method which was introduced in Python 2.7.

    :param timedelta: the timedelta
    :type timedelta: :class:`datetime.timedelta`
    :returns: the total number of seconds contained in the duration

    """
    if not isinstance(timedelta, datetime.timedelta):
        raise TypeError('expected a datetime.timedelta, not ' +
                        repr(timedelta))
    elif hasattr(timedelta, 'total_microseconds'):
        return timedelta.total_microseconds()
    microsec = timedelta.microseconds
    sec = timedelta.seconds
    days = timedelta.days
    return (microsec + (sec + days * 24 * 3600) * 10 ** 6) / 10 ** 6

