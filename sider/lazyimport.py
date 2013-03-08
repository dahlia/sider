""":mod:`sider.lazyimport` --- Lazily imported modules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides a :class:`types.ModuleType`-like proxy object for submodules of
the :mod:`sider` package.  These are for workaround circular importing.

"""
from __future__ import absolute_import
import types


class DeferredModule(types.ModuleType):
    """The deferred version of :class:`types.ModuleType`.
    Under the hood it imports the actual module when it actually has to.

    """

    def __init__(self, *args, **kwargs):
        super(DeferredModule, self).__init__(*args, **kwargs)
        self.__actual_module__ = None

    def __getattr__(self, name):
        mod = self.__actual_module__
        if mod is None:
            mod = __import__(self.__name__)
            mod = reduce(getattr, self.__name__.split('.')[1:], mod)
            self.__actual_module__ = mod
        return getattr(mod, name)

    def __repr__(self):
        return '<deferred module {0!r}>'.format(self.__name__)


#: (:class:`DeferredModule`) Alias of :mod:`sider.session`.
session = DeferredModule('sider.session')

#: (:class:`DeferredModule`) Alias of :mod:`sider.types`.
types = DeferredModule('sider.types')

#: (:class:`DeferredModule`) Alias of :mod:`sider.transaction`.
transaction = DeferredModule('sider.transaction')

#: (:class:`DeferredModule`) Alias of :mod:`sider.hash`.
hash = DeferredModule('sider.hash')

#: (:class:`DeferredModule`) Alias of :mod:`sider.list`.
list = DeferredModule('sider.list')

#: (:class:`DeferredModule`) Alias of :mod:`sider.set`.
set = DeferredModule('sider.set')

#: (:class:`DeferredModule`) Alias of :mod:`sider.sortedset`.
sortedset = DeferredModule('sider.sortedset')

#: (:class:`DeferredModule`) Alias of :mod:`sider.datetime`.
datetime = DeferredModule('sider.datetime')

#: (:class:`DeferredModule`) Alias of :mod:`sider.warnings`.
warnings = DeferredModule('sider.warnings')

#: (:class:`DeferredModule`) Alias of :mod:`sider.exceptions`.
exceptions = DeferredModule('sider.exceptions')

#: (:class:`DeferredModule`) Alias of :mod:`sider.version`.
version = DeferredModule('sider.version')


__all__ = tuple(name for name, value in globals().items()
                     if isinstance(value, DeferredModule))

