""":mod:`sider.warnings` --- Warning categories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module defines several custom warning category classes.

"""


class PerformanceWarning(RuntimeWarning):
    """The category for warnings about performance worries.  Operations
    that warn this category would work but be inefficient.

    """


