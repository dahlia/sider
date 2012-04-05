""":mod:`sider.threadlocal` --- Thread locals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from threading import get_ident
    except ImportError:
        from dummy_thread import get_ident

