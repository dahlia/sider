""":mod:`sider.transaction` --- Transaction handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from redis.client import WatchError
from .session import Session


class Transaction(object):
    """Transaction block.

    :param session: a session object
    :type session: :class:`~sider.session.Session`
    :param keys: the list of keys
    :type keys: :class:`collections.Iterable`

    """

    def __init__(self, session, keys):
        if not isinstance(session, Session):
            raise TypeError('session must be a sider.session.Session instance'
                            ', not ' + repr(session))
        self.session = session
        self.keys = list(keys)

    def __enter__(self):
        context = self.session.context_locals
        if context['transaction'] is not None:
            raise DoubleTransactionError('there is already a transaction for '
                                         ' the session ' + repr(self.session))
        context['transaction'] = self
        client = self.session.client
        context['original_client'] = client
        pipeline = client.pipeline()
        self.session.client = pipeline
        pipeline.watch(*self.keys)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value is None:
            try:
                self.session.client.execute()
            except WatchError:
                raise  # FIXME
        else:
            self.session.client.reset()
        context = self.session.context_locals
        context['transaction'] = None
        self.session.client = context['original_client']
        del context['original_client']

    def begin_commit(self):
        """Explicitly marks the transaction beginning to commit from this.
        From this to end of a transaction, any query operations will raise
        :exc:`CommitError`.

        """
        self.session.client.multi()


class TransactionError(Exception):
    """Transaction-related error."""


class DoubleTransactionError(TransactionError):
    """Error raised when transactions are doubly tried for a session."""


class CommitError(TransactionError):
    """Error raised when any query operations are tried during commit phase."""

