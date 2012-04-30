""":mod:`sider.warnings` --- Warning categories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module defines several custom warning category classes.

"""


class SiderWarning(Warning):
    """All warning classes used by Sider extend this base class."""


class PerformanceWarning(SiderWarning, RuntimeWarning):
    """The category for warnings about performance worries.  Operations
    that warn this category would work but be inefficient.

    """


class TransactionWarning(SiderWarning, RuntimeWarning):
    """The category for warnings about transactions."""

