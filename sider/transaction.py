""":mod:`sider.transaction` --- Transaction handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. todo::

   Roughly planned roadmap:

   - Make :meth:`~Transaction.begin_commit()` implicit.
   - Mark methods whether it is query or manipulative.
   - Make an explicit method for watching and
     make :meth:`~Transaction.__enter__()` to use that method.
   - Make it iterative; it loops until it commit successfully without any
     conflicts.

"""
from __future__ import absolute_import
from redis.client import WatchError
from .session import Session
from .exceptions import DoubleTransactionError, ConflictError


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
        try:
            if exc_value is None:
                try:
                    self.session.client.execute()
                except WatchError:
                    raise ConflictError('the transaction has met conflicts; '
                                        'retry')
            else:
                self.session.client.reset()
            context = self.session.context_locals
            context['transaction'] = None
            self.session.client = context['original_client']
        finally:
            del context['original_client']

    def begin_commit(self):
        """Explicitly marks the transaction beginning to commit from this.
        From this to end of a transaction, any query operations will raise
        :exc:`~sider.exceptions.CommitError`.

        """
        self.session.client.multi()

