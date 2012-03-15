""":mod:`sider.datetime` --- Date and time related utilities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For minimum support of time zones, without adding any external dependencies
e.g. pytz_, Sider had to implement :class:`Utc` class which is a subtype of
:class:`datetime.tzinfo`.

Because :mod:`datetime` module provided by the Python standard library
doesn't contain UTC or any other :class:`~datetime.tzinfo` subtype
implementations.  (A funny thing is that the documentation of :mod:`datetime`
module show an example of how to implement UTC :class:`~datetime.tzinfo`.)

If you want more various time zones support use the third-party pytz_
package.

.. _UTC: http://en.wikipedia.org/wiki/Coordinated_Universal_Time
.. _pytz: http://pytz.sourceforge.net/

"""
from __future__ import absolute_import
import datetime


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

