""":mod:`sider.exceptions` --- Exception classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module defines several custom exception classes.

"""


class SiderError(Exception):
    """All exception classes Sider raises extend this base class."""


class TransactionError(SiderError):
    """Transaction-related error."""


class DoubleTransactionError(TransactionError):
    """Error raised when transactions are doubly tried for a session."""


class CommitError(TransactionError):
    """Error raised when any query operations are tried during commit phase."""


class ConflictError(TransactionError):
    """Error rasied when the transaction has met conflicts."""

