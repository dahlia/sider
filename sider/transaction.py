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
import traceback
from redis.client import WatchError
from .exceptions import DoubleTransactionError, ConflictError
from .warnings import TransactionWarning
from . import lazyimport


class Transaction(object):
    """Transaction block.  It's a low-level primitive for Sider transaction.
    In most case what you actually need to use is probably
    :meth:`Session.transaction() <sider.session.Session.transaction>` method.

    :param session: a session object
    :type session: :class:`~sider.session.Session`
    :param keys: the list of keys
    :type keys: :class:`collections.Iterable`

    .. todo

       Make the ``keys`` parameter optional if possible.

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
            raise DoubleTransactionError(
                'there is already a transaction for the session ' +
                repr(self.session) + self.format_enter_stack()
            )
        context['transaction'] = self
        client = self.session.client
        context['original_client'] = client
        pipeline = client.pipeline()
        self.session.client = pipeline
        pipeline.watch(*self.keys)
        if self.session.verbose_transaction_error:
            self.enter_stack = traceback.format_stack()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if exc_value is None:
                try:
                    self.session.client.execute()
                except WatchError:
                    self.session.client.reset()
                    raise ConflictError('the transaction has met conflicts; '
                                        'retry')
            else:
                self.session.client.reset()
        finally:
            self.commit_phase = False
            context = self.session.context_locals
            context['transaction'] = None
            self.session.client = context['original_client']
            del context['original_client']

    def begin_commit(self, _stacklevel=1):
        """Explicitly marks the transaction beginning to commit from this.
        From this to end of a transaction, any query operations will raise
        :exc:`~sider.exceptions.CommitError`.

        """
        if self.commit_phase:
            warnings.warn('the transaction already is on commit phase; '
                          'begin_commit() method seems called twice or more' +
                          self.format_commit_stack(),
                          category=TransactionWarning, stacklevel=2)
            return
        self.commit_phase = True
        if self.session.verbose_transaction_error:
            self.commit_stack = traceback.format_stack()
        self.session.client.multi()

    def format_enter_stack(self, indent=4,
                           title='Traceback where the transaction entered:'):
        """Makes :attr:`enter_stack` text readable.
        If its :attr:`session.verbose_transaction_error
        <sider.session.Session.verbose_transaction_error>` is not ``True``,
        it will simply return an empty string.

        :param indent: the number of space character for indentation.
                       default is 4
        :type indent: :class:`numbers.Integral`
        :param title: the title string of the formatted traceback. optional
        :type title: :class:`basestring`
        :returns: the formatted :attr:`enter_stack` text
        :rtype: :class:`basestring`

        .. note::

           It's totally for internal use.

        """
        if self.session.verbose_transaction_error:
            try:
                stack = self.enter_stack
            except AttributeError:
                return ''
            indent_str = ' ' * indent
            tb = '\n'.join(indent_str + line
                           for frame in stack
                           for line in frame.splitlines())
            return '\n{0}{1}\n{2}'.format(indent_str, title, tb)
        return ''

    def format_commit_stack(self, indent=4,
                            title='Traceback of previous begin_commit() call:'):
        """Makes :attr:`commit_stack` text readable.
        If its :attr:`session.verbose_transaction_error
        <sider.session.Session.verbose_transaction_error>` is not ``True``,
        it will simply return an empty string.

        :param indent: the number of space character for indentation.
                       default is 4
        :type indent: :class:`numbers.Integral`
        :param title: the title string of the formatted traceback. optional
        :type title: :class:`basestring`
        :returns: the formatted :attr:`commit_stack` text
        :rtype: :class:`basestring`

        .. note::

           It's totally for internal use.

        """
        if self.session.verbose_transaction_error:
            try:
                stack = self.commit_stack
            except AttributeError:
                return ''
            indent_str = ' ' * indent
            tb = '\n'.join(indent_str + line
                           for frame in stack
                           for line in frame.splitlines())
            return '\n{0}{1}\n{2}'.format(indent_str, title, tb)
        return ''


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

