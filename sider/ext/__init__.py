""":mod:`sider.ext` --- Extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This package is a *virtual* namespace package that forwards
:mod:`sider.ext.mycontrib` to :mod:`sider_mycontrib`.

If you are writing a user-contributed module for Sider,
simply name your module/package like :mod:`sider_modulename`
and then it becomes importable by :mod:`sider.ext.modulename`.

.. This approach is influeced by Flask's one.

"""
import sys


class ExtensionImporter(object):
    """Importer that forwards a submodule which belongs to ``namespace``
    (i.e. :mod:`sider.ext`) to an actual alias module (i.e. ``alias``).

    For example, where ``namespace`` is ``'sider.ext'`` and
    ``alias`` is ``'sider_{0}'``::

        from sider.ext import mycontrib

    is equivalent to::

        import sider_mycontrib as mycontrib

    .. note::

       It is only for internal use.

    """

    def __init__(self, namespace, alias, sys):
        self.namespace = namespace
        self.prefix = namespace + '.'
        self.alias = alias
        self.sys = sys

    def find_module(self, fullname, path=None):
        if fullname.startswith(self.prefix):
            return self

    def load_module(self, fullname):
        try:
            return self.sys.modules[fullname]
        except KeyError:
            pass
        subname = fullname[len(self.prefix):]
        actual = self.alias.format(subname)
        try:
            __import__(actual)
        except ImportError:
            raise ImportError('No module named ' + repr(fullname))
        module = self.sys.modules[actual]
        self.sys.modules[fullname] = module
        if '.' not in subname:
            setattr(self.sys.modules[self.namespace], subname, module)
        return module


importer = ExtensionImporter(__name__, 'sider_{0}', sys)
sys.meta_path.append(importer)
del sys, importer, ExtensionImporter

