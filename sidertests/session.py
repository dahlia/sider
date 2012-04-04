from attest import Tests, assert_hook, raises
from .env import NInt, init_session, key
from sider.types import (Set as SetT, List as ListT, Integer)
from sider.set import Set
from sider.list import List


tests = Tests()
tests.context(init_session)


@tests.test
def getset_int(session):
    int_ = session.set(key('test_session_getset_int'), 1234, Integer)
    assert int_ == 1234
    int_ = session.get(key('test_session_getset_int'), Integer)
    assert int_ == 1234


@tests.test
def getset_nint(session):
    int_ = session.set(key('test_session_getset_nint'), 1234, NInt)
    assert int_ == 1234
    int_ = session.get(key('test_session_getset_nint'), NInt)
    assert int_ == 1234


@tests.test
def getset_set(session):
    set_ = session.set(key('test_session_getset_set'), set('abc'), SetT)
    assert isinstance(set_, Set)
    assert set(set_) == set(['a', 'b', 'c'])
    set_ = session.get(key('test_session_getset_set'), SetT)
    assert isinstance(set_, Set)
    assert set(set_) == set(['a', 'b', 'c'])
    with raises(TypeError):
        session.set(key('test_session_getset_set'), 1234, SetT)
    with raises(TypeError):
        session.set(key('test_session_getset_set'), 'abc', SetT)


@tests.test
def getset_list(session):
    lst = session.set(key('test_session_getset_list'), 'abc', ListT)
    assert isinstance(lst, List)
    assert list(lst) == ['a', 'b', 'c']
    lst = session.get(key('test_session_getset_list'), ListT)
    assert isinstance(lst, List)
    assert list(lst) == ['a', 'b', 'c']
    with raises(TypeError):
        session.set(key('test_session_getset_list'), 1234, ListT)

