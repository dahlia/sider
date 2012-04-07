from attest import Tests, assert_hook, raises
from .env import NInt, get_session, key
from sider.types import List
from sider.transaction import Transaction, DoubleTransactionError


tests = Tests()


@tests.test
def raw_transaction():
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


@tests.test
def double_transaction_error():
    session = get_session()
    keyid = key('test_transaction_double_error')
    with Transaction(session, [keyid]):
        with raises(DoubleTransactionError):
            with Transaction(session, [keyid]):
                pass

