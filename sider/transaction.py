""":mod:`sider.transaction` --- Transaction handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every Persist object provided by Sider can be used within
transactions.  You can atomically commit multiple operations.

Under the hood, transaction blocks are simply looped until objects
the transaction deals with haven't been faced any conflicts with
other sessions/transactions.  If there are no concurrent touches
to ``names`` in the following transaction::

    def block(trial, transaction):
        names.append(new_name)
    session.transaction(block)

it will be successfully committed.  Otherwise, it retries the
whole transaction ``block``.  You can easily prove this by just
printing ``trial`` (the first argument of the block function)
inside the transaction block.  It will print one or more retrial
counting numbers.

This means you shouldn't do I/O in the transaction block.
Your I/O could be executed two or more times.  Do I/O after or
before transaction blocks instead.

There are two properties of every operation: :func:`query` or
:func:`manipulative` or both.  For example, :meth:`Hash.get()
<sider.hash.Hash.get>` method is a query operation.
On the other hand, :meth:`Set.add() <sider.set.Set.add>` method
is manipulative.  There is a rule of transaction: query operations
can't be used after manipulative operations.  For example,
the following transaction block has no problem::

    # Atomically wraps an existing string value of the specific
    # key of a hash.
    hash_ = session.get('my_hash', Hash)
    def block(trial, transaction):
        current_value = hash_['my_key']  # [query operation]
        updated_value = '(' + current_value + ')'
        hash_['my_key'] = updated_value  # [manipulative operation]
    session.transaction(block)

while the following raises a :exc:`~sider.exceptions.CommitError`::

    hash_ = session.get('my_hash', Hash)
    def block(trial, transaction):
        current_value = hash_['my_key']   # [query operation]
        updated_value = '(' + current_value + ')'
        hash_['my_key'] = updated_value   # [manipulative operation]
        # The following statement raises CommitError because
        # it contains a query operation.
        current_value2 = hash_['my_key2'] # [query operation]
        updated_value2 = '(' + current_value + ')'
        hash_['my_key'] = updated_value2  # [manipulative operation]
    session.transaction(block)

.. seealso::

   `Redis Transactions <http://redis.io/topics/transactions>`_
      The Redis documentation that explains about its transactions.

"""
from __future__ import absolute_import
import sys
import warnings
import functools
import traceback
from redis.client import WatchError
from .exceptions import DoubleTransactionError, ConflictError
from .warnings import SiderWarning, TransactionWarning
from . import lazyimport


class Transaction(object):
    """Transaction block.

    :param session: a session object
    :type session: :class:`~sider.session.Session`
    :param keys: the list of keys
    :type keys: :class:`collections.Iterable`

    """

    def __init__(self, session, keys=frozenset()):
        if not isinstance(session, lazyimport.session.Session):
            raise TypeError('session must be a sider.session.Session instance'
                            ', not ' + repr(session))
        self.session = session
        self.keys = set(keys)
        self.initial_keys = frozenset(keys)
        self.commit_phase = False
        self.entered = False

    def __enter__(self):
        context = self.session.context_locals
        if context['transaction'] is not None:
            raise DoubleTransactionError(
                'there is already a transaction for the session ' +
                repr(self.session) + self.format_enter_stack()
            )
        self.entered = True
        context['transaction'] = self
        client = self.session.client
        context['original_client'] = client
        self.session.client = client.pipeline()
        self.watch(self.initial_keys, initialize=True)
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
            self.entered = False

    def __iter__(self):
        """You can more explictly execute (and retry) a routine in
        the transaction than using :meth:`__call__()`.

        It returns a generator that yields an integer which represents
        its (re)trial count (from 0) until the transaction doesn't
        face :exc:`~sider.exceptions.ConflictError`.

        For example::

            for trial in transaction:
                list_[0] = list_[0].upper()

        :raises sider.exceptions.DoubleTransactionError:
           when any transaction has already being executed for a session

        """
        transaction = self.session.current_transaction
        if transaction is None:
            trial = 0
            while 1:
                try:
                    with self:
                        yield trial
                except ConflictError:
                    trial += 1
                    continue
                break
        else:
            raise DoubleTransactionError(
                'transactions are tried doubly for a session at a time' +
                transaction.format_enter_stack()
            )

    def __call__(self, block, keys=frozenset(), ignore_double=False):
        """Executes a ``block`` in the transaction::

            def block(trial, transaction):
                list_[0] = list_[0].upper()
            transaction(block)

        :param block: a function to execute in a transaction.
                      see the signature explained in the below:
                      :func:`block()`
        :type block: :class:`collections.Callable`
        :param keys: a list of keys to watch
        :type keys: :class:`collections.Iterable`
        :param ignore_double: don't raise any error even
                              if any transaction has already being
                              executed for a session.
                              default is ``False``
        :type ignore_double: :class:`bool`
        :raises sider.exceptions.DoubleTransactionError:
           when any transaction has already being executed for a session
           and ``ignore_double`` is ``False``

        .. function:: block(trial, transaction)

           :param trial: the number of trial count.  starts from 0
           :type trial: :class:`numbers.Integral`
           :param transaction: the current transaction object
           :type transaction: :class:`~sider.transaction.Transaction`

        """
        try:
            for trial in self:
                self.watch(keys)
                block(trial, self)
        except DoubleTransactionError:
            if ignore_double:
                t = self.session.current_transaction
                t.watch(keys)
                block(0, None)
            else:
                raise
        except:
            # PyPy 1.8 doesn't seem to call __exit__() when with: block
            # is used inside generator.  To workaround we have to maintain
            # the attribute named .entered which represents whether "it was
            # acutally cleaned up, right?"
            # See also: https://bugs.pypy.org/issue1126
            if self.entered:
                self.__exit__(*sys.exc_info())
            raise

    def watch(self, keys, initialize=False):
        """Watches more ``keys``.

        :param keys: a set of keys to watch more
        :type keys: :class:`collections.Iterable`
        :param initialize: initializes the set of watched keys
                           if it is ``True``.  default is ``False``.
                           option only for internal use
        :type initialize: :class:`bool`

        """
        if isinstance(keys, basestring):
            warnings.warn('you could probably want to watch [{0!r}] instead of '
                          '{1!r}; do not directly pass a string but a list of '
                          'string to be explicit'.format(keys, list(keys)),
                          category=SiderWarning, stacklevel=2)
        keys = set(keys)
        if initialize:
            self.keys = keys
        else:
            keys -= self.keys
        if keys:
            self.session.client.watch(*keys)
        if not initialize:
            self.keys |= keys

    def begin_commit(self, _stacklevel=1):
        """Explicitly marks the transaction beginning to commit from this.
        From this to end of a transaction, any query operations will raise
        :exc:`~sider.exceptions.CommitError`.

        """
        if self.commit_phase:
            warnings.warn('the transaction already is on commit phase; '
                          'begin_commit() method seems called twice or more' +
                          self.format_commit_stack(),
                          category=TransactionWarning,
                          stacklevel=1 + _stacklevel)
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
    :rtype: :class:`collections.Callable`

    """
    @functools.wraps(function)
    def marked(self, *args, **kwargs):
        self.session.mark_manipulative([self.key] if hasattr(self, 'key')
                                                  else [])
        return function(self, *args, **kwargs)
    return marked


def query(function):
    """The decorator that marks the method query.

    :param function: the method to mark
    :type function: :class:`collections.Callable`
    :returns: the marked method
    :rtype: :class:`collections.Callable`

    """
    @functools.wraps(function)
    def marked(self, *args, **kwargs):
        self.session.mark_query([self.key] if hasattr(self, 'key') else [])
        return function(self, *args, **kwargs)
    return marked

