""":mod:`sider.threadlocal` --- Thread locals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides a small thread/greenlet local object.
Why we don't simply use the built-in :class:`threading.local`
is there's the case of using :mod:`greenlet`, the non-standard
but de facto standard coroutine module for Python, in real world.
(For example, widely used networking libraries like :mod:`gevent`
or :mod:`eventlet` heavily use :mod:`greenlet`.)

:class:`LocalDict` which this module offers isn't aware of only
threads but including greenlets.

.. note::

   This module is inspired by :mod:`werkzeug.local` module but
   only things we actually need are left.

.. function:: get_ident()

   Gets the object that can identify of the current thread/greenlet.
   It can return an object that can be used as dictionary keys.

   :returns: a something that can identify of the current thread or
             greenlet

   .. note::

      Under the hood it is an alias of :func:`greenlet.getcurrent()`
      function if it is present.  Or it will be aliased to
      :func:`thread.get_ident()` or :func:`dummy_thread.get_ident()`
      that both are a part of standard if :mod:`greenlet` module
      is not present.

      However that's all only an implementation detail and so
      it may changed in the future.  Client codes that use
      :func:`sider.threadlocal.get_ident()` have to be written
      on only assumptions that it guarantees: *it returns an object
      that identify of the current thread/greenlet and be used as
      dictionary keys.*

"""
import collections
try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from threading import get_ident
    except ImportError:
        from dummy_thread import get_ident


class LocalDict(collections.MutableMapping):
    """A thread/greenlet-local dictionary.
    It implements :class:`collections.MutableMapping` protocol and so
    behaves almost like built-in :class:`dict` objects.

    :param mapping: the initial items.  all locals have the same
                    this initial items
    :type mapping: :class:`collections.Mapping`,
                   :class:`collections.Iterable`
    :param \*\*keywords: the initial keywords.  all locals have the
                         same this initial items

    """

    __slots__ = 'idents', 'initial'

    def __init__(self, mapping=[], **keywords):
        self.idents = {}
        self.initial = dict(mapping, **keywords)

    @property
    def current(self):
        ident = get_ident()
        try:
            return self.idents[ident]
        except KeyError:
            d = self.initial.copy()
            self.idents[ident] = d
            return d

    def __len__(self):
        return len(self.current)

    def __iter__(self):
        return iter(self.current)

    def __contains__(self, value):
        return value in self.current

    def __getitem__(self, key):
        return self.current[key]

    def __setitem__(self, key, value):
        self.current[key] = value

    def __delitem__(self, key):
        del self.current[key]

    def copy(self):
        return self.current.copy()

    def get(self, key, default=None):
        return self.current.get(key, default)

    def has_key(self, key):
        return key in self

    def items(self):
        return self.current.items()

    def iteritems(self):
        return self.current.iteritems()

    def iterkeys(self):
        return self.current.keys()

    def itervalues(self):
        return self.current.itervalues()

    def keys(self):
        return self.current.keys()

    def values(self):
        return self.current.values()

    def clear(self):
        self.current.clear()

    def pop(self, key, *args):
        return self.current.pop(key, *args)

    def popitem(self):
        return self.current.popitem()

    def setdefault(self, key, default=None):
        self.current.setdefault(key, default)

    def update(self, mapping, **keywords):
        self.current.update(mapping, **keywords)

