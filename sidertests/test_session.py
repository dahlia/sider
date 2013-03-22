import warnings
from redis.client import StrictRedis, Redis
from pytest import raises
from .env import NInt, get_client, key
from .env import session
from sider.session import Session
from sider.types import (Set as SetT,
                         List as ListT,
                         Hash as HashT,
                         SortedSet as SortedSetT,
                         Integer)
from sider.set import Set
from sider.list import List
from sider.hash import Hash
from sider.sortedset import SortedSet


class CustomRedis(StrictRedis):
    """A custom subclass of StrictRedis for test."""


def ensure_encoding_error(excinfo):
    """Ensure that given error is raised from :meth:`~Bulk.encode()`

    .. seealso:: <https://gist.github.com/Kroisse/5211709>

    """
    assert 'argument after * must be a sequence' not in str(excinfo.value), \
        'Ensure to not use an iterable object as a variadic arugments'
    assert excinfo.traceback[-1].name == 'encode'


def test_warn_old_client():
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


def test_getset_int(session):
    int_ = session.set(key('test_session_getset_int'), 1234, Integer)
    assert int_ == 1234
    int_ = session.get(key('test_session_getset_int'), Integer)
    assert int_ == 1234


def test_getset_nint(session):
    int_ = session.set(key('test_session_getset_nint'), 1234, NInt)
    assert int_ == 1234
    int_ = session.get(key('test_session_getset_nint'), NInt)
    assert int_ == 1234


def test_getset_set(session):
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
    with raises(TypeError) as excinfo:
        session.set(key('test_session_getset_set'), set([1, 2, 3]), SetT)
    ensure_encoding_error(excinfo)


def test_set_empty_set(session):
    set_ = session.set(key('test_session_set_empty_set'), set(), SetT)
    assert isinstance(set_, Set)
    assert set(set_) == set()


def test_getset_list(session):
    lst = session.set(key('test_session_getset_list'), 'abc', ListT)
    assert isinstance(lst, List)
    assert list(lst) == ['a', 'b', 'c']
    lst = session.get(key('test_session_getset_list'), ListT)
    assert isinstance(lst, List)
    assert list(lst) == ['a', 'b', 'c']
    with raises(TypeError):
        session.set(key('test_session_getset_list'), 1234, ListT)
    with raises(TypeError) as excinfo:
        session.set(key('test_session_getset_list'), [1, 2, 3], ListT)
    ensure_encoding_error(excinfo)


def test_set_empty_list(session):
    lst = session.set(key('test_session_set_empty_list'), [], ListT)
    assert isinstance(lst, List)
    assert list(lst) == []


def test_getset_hash(session):
    hash_ = session.set(key('test_session_getset_hash'),
                        {'a': 'b', 'c': 'd'}, HashT)
    assert isinstance(hash_, Hash)
    assert dict(hash_) == {'a': 'b', 'c': 'd'}
    hash_ = session.get(key('test_session_getset_hash'), HashT)
    assert isinstance(hash_, Hash)
    assert dict(hash_) == {'a': 'b', 'c': 'd'}
    with raises(TypeError):
        session.set(key('test_session_getset_hash'), 1234, HashT)
    with raises(TypeError):
        session.set(key('test_session_getset_hash'), 'abc', HashT)
    with raises(TypeError) as excinfo:
        session.set(key('test_session_getset_hash'),
                    {'a': 1, 'b': 2}, HashT)
    ensure_encoding_error(excinfo)


def test_set_empty_hash(session):
    hash_ = session.set(key('test_session_set_empty_hash'), {}, HashT)
    assert isinstance(hash_, Hash)
    assert dict(hash_) == {}


def test_set_empty_sortedset(session):
    set_ = session.set(key('test_session_set_empty_sortedset'),
                       set(), SortedSetT)
    assert isinstance(set_, SortedSet)
    assert dict(set_) == {}


def test_version_info(session):
    assert isinstance(session.server_version, str)
    assert isinstance(session.server_version_info, tuple)
    for v in session.server_version_info:
        assert isinstance(v, int)
    version_str = '.'.join(map(str, session.server_version_info))
    assert session.server_version == version_str
