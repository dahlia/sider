Sider Changelog
===============

Version 0.2.0
-------------

- Added :mod:`sider.transaction` module.
- Added :mod:`sider.sortedset` module.
- Added :class:`sider.types.SortedSet` type.
- Added :class:`sider.types.Time` and :class:`sider.types.TZTime` types.
- Added :class:`sider.types.TimeDelta` type.
- Added :mod:`sider.threadlocal` module.
- Added :attr:`sider.session.Session.verbose_transaction_error` option.


Version 0.1.3
-------------

Released on April 21, 2012.  Pre-alpha release.

- Now :class:`sider.hash.Hash` objects show their contents for :func:`repr()`.
- Now persist objects show their key name for :func:`repr()`.
- Added :data:`sider.lazyimport.exceptions` deferred module.


Version 0.1.2
-------------

Released on April 11, 2012.  Pre-alpha release.

- Now :class:`sider.session.Session` takes :class:`redis.client.StrictRedis`
  object instead of :class:`redis.client.Redis` which is deprecated.
- Added :mod:`sider.exceptions` module.
- Added :class:`sider.warnings.SiderWarning` base class.
- Fixed a bug of :meth:`sider.list.List.insert()` for index -1.
  Previously it simply appends an element to the list (and that is an
  incorrect behavior), but now it inserts an element into the right before
  of its last element.


Version 0.1.1
-------------

Released on March 29, 2012.  Pre-alpha release.

- Added :class:`sider.types.Boolean` type.
- Added :class:`sider.types.Date` type.
- Added :class:`sider.datetime.FixedOffset` tzinfo subtype.
- Added :class:`sider.types.DateTime` and
  :class:`~sider.types.TZDateTime` types.
- Now you can check the version by this command:
  ``python -m sider.version``.


Version 0.1.0
-------------

Released on March 23, 2012.  Pre-alpha release.

