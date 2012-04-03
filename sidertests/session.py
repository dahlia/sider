import warnings
from redis.client import StrictRedis, Redis
from attest import Tests, assert_hook, raises
from .env import NInt, get_client, get_session, key
from sider.session import Session
from sider.types import (Set as SetT, List as ListT, Integer)
from sider.set import Set
from sider.list import List


tests = Tests()


class CustomRedis(StrictRedis):
    """A custom subclass of StrictRedis for test."""


@tests.test
def warn_old_client():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        Session(get_client(cls=CustomRedis))
        assert len(w) == 0
    old_client = get_client(cls=Redis)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        Session(old_client)
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)


@tests.test
def getset_int():
    session = get_session()
    int_ = session.set(key('test_session_getset_int'), 1234, Integer)
    assert int_ == 1234
    int_ = session.get(key('test_session_getset_int'), Integer)
    assert int_ == 1234


@tests.test
def getset_nint():
    session = get_session()
    int_ = session.set(key('test_session_getset_nint'), 1234, NInt)
    assert int_ == 1234
    int_ = session.get(key('test_session_getset_nint'), NInt)
    assert int_ == 1234


@tests.test
def getset_set():
    session = get_session()
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
def getset_list():
    session = get_session()
    lst = session.set(key('test_session_getset_list'), 'abc', ListT)
    assert isinstance(lst, List)
    assert list(lst) == ['a', 'b', 'c']
    lst = session.get(key('test_session_getset_list'), ListT)
    assert isinstance(lst, List)
    assert list(lst) == ['a', 'b', 'c']
    with raises(TypeError):
        session.set(key('test_session_getset_list'), 1234, ListT)

