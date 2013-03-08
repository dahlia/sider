import warnings
from pytest import raises
from .env import get_session, key
from sider.types import List
from sider.transaction import Transaction
from sider.exceptions import CommitError, ConflictError, DoubleTransactionError
from sider.warnings import SiderWarning


def test_raw_transaction():
    session1 = get_session()
    session2 = get_session()
    keyid = key('test_transaction_raw')
    list1 = session1.set(keyid, 'abc', List)
    list2 = session2.get(keyid, List)
    with Transaction(session1, [keyid]) as t:
        assert isinstance(t, Transaction)
        assert list1[:] == ['a', 'b', 'c']
        assert list2[:] == ['a', 'b', 'c']
        t.begin_commit()
        list1.append('d')
        assert list2[:] == ['a', 'b', 'c']
    assert list1[:] == list2[:] == ['a', 'b', 'c', 'd']


def test_transaction_iterate():
    session = get_session()
    session2 = get_session()
    keyid = key('test_transaction_iterate')
    list1 = session.set(keyid, 'abc', List)
    list2 = session2.get(keyid, List)
    for trial in Transaction(session, [keyid]):
        up = list1[0].upper()
        if trial < 3:
            list2.append('x')
        list1[0] = up
    assert list1[:] == list2[:] == list('Abcxxx')
    assert trial == 3


def test_transaction_call():
    session = get_session()
    session2 = get_session()
    keyid = key('test_transaction_call')
    list1 = session.set(keyid, 'abc', List)
    list2 = session2.get(keyid, List)
    t = Transaction(session, [keyid])
    total_trial = [0]
    def block(trial, transaction):
        total_trial[0] = trial
        up = list1[0].upper()
        if trial < 3:
            list2.append('x')
        list1[0] = up
    t(block)
    assert list1[:] == list2[:] == list('Abcxxx')
    assert total_trial[0] == 3


def test_automatic_watch():
    session = get_session()
    session2 = get_session()
    keyid = key('test_transaction_automatic_watch')
    list_ = session.set(keyid, 'abc', List)
    list2 = session2.get(keyid, List)
    with raises(ConflictError):
        with Transaction(session):
            list_.append('d')
            list2.append('e')
    # Transation.keys have to be initialized for each context:
    t = Transaction(session)
    with t:
        list_.append('d')
    listx = session.set(key('test_transaction_automatic_watch2'), 'abc', List)
    with t:
        listx.append('a')
        list2.append('b')
    with t:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            t.watch('asdf')
            assert len(w) == 1
            assert issubclass(w[0].category, SiderWarning)


def test_conflict_error():
    session = get_session()
    session2 = get_session()
    keyid = key('test_transaction_conflict_error')
    list_ = session.set(keyid, 'abc', List)
    list2 = session2.get(keyid, List)
    with raises(ConflictError):
        with Transaction(session, [keyid]):
            list_.append('d')
            list2.append('e')


def test_commit_error():
    session = get_session()
    keyid = key('test_transaction_commit_error')
    list_ = session.set(keyid, 'abc', List)
    try:
        with Transaction(session, [keyid]):
            list_.append('d')
            try:
                list(list_)
            except CommitError:
                raise
            else:
                assert False, 'expected CommitError'
    except CommitError:
        pass
    assert list_[:] == list('abc'), 'transaction must be rolled back'


def test_double_transaction_error():
    session = get_session()
    keyid = key('test_transaction_double_error')
    with Transaction(session, [keyid]):
        with raises(DoubleTransactionError):
            with Transaction(session, [keyid]):
                pass
