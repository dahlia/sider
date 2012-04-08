""":mod:`sider.transaction` --- Transaction handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. todo::

   Roughly planned roadmap:

   - Mark methods wether it is manpulative or query.
   - Make it iterative; it loops until it commit successfully without any
     conflicts.

"""
from __future__ import absolute_import
import warnings
import functools
from redis.client import WatchError
from .exceptions import DoubleTransactionError, ConflictError
from .warnings import TransactionWarning
from . import lazyimport


class Transaction(object):
    """Transaction block.

    :param session: a session object
    :type session: :class:`~sider.session.Session`
    :param keys: the list of keys
    :type keys: :class:`collections.Iterable`

    """

    def __init__(self, session, keys):
        if not isinstance(session, lazyimport.session.Session):
            raise TypeError('session must be a sider.session.Session instance'
                            ', not ' + repr(session))
        self.session = session
        self.keys = list(keys)
        self.commit_phase = False

    def __enter__(self):
        context = self.session.context_locals
        if context['transaction'] is not None:
            raise DoubleTransactionError('there is already a transaction for '
                                         'the session ' + repr(self.session))
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
            self.commit_phase = False
            context = self.session.context_locals
            context['transaction'] = None
            self.session.client = context['original_client']
        finally:
            del context['original_client']

    def begin_commit(self, _stacklevel=1):
        """Explicitly marks the transaction beginning to commit from this.
        From this to end of a transaction, any query operations will raise
        :exc:`~sider.exceptions.CommitError`.

        """
        if self.commit_phase:
            warnings.warn('the transaction already is on commit phase; '
                          'begin_commit() method seems called twice or more',
                          category=TransactionWarning, stacklevel=2)
            return
        self.commit_phase = True
        self.session.client.multi()


def manipulative(function):
    """The decorator that marks the method manipulative.

    :param function: the method to mark
    :type function: :class:`collections.Callable`
    :returns: the marked method
    :rtype: :class:`collections.Callable

    """
    @functools.wraps(function)
    def marked(self, *args, **kwargs):
        self.session.mark_manipulative()
        return function(self, *args, **kwargs)
    return marked


def query(function):
    """The decorator that marks the method query.

    :param function: the method to mark
    :type function: :class:`collections.Callable`
    :returns: the marked method
    :rtype: :class:`collections.Callable

    """
    @functools.wraps(function)
    def marked(self, *args, **kwargs):
        self.session.mark_query()
        return function(self, *args, **kwargs)
    return marked

