import warnings
from attest import Tests, assert_hook, raises
from .env import get_session, key
from sider.types import List, Integer
from sider.warnings import PerformanceWarning


tests = Tests()


@tests.test
def iterate():
    session = get_session()
    view = session.set(key('test_list_iterate'), 'abc', List)
    assert ['a', 'b', 'c'] == list(view)
    view = session.set(key('test_listx_iterate'), [1, 2, 3], List(Integer))
    assert [1, 2, 3] == list(view)


@tests.test
def length():
    session = get_session()
    view = session.set(key('test_list_length'), 'abc', List)
    assert len(view) == 3


@tests.test
def get():
    session = get_session()
    view = session.set(key('test_list_get'), 'abc', List)
    assert 'a' == view[0]
    assert 'b' == view[1]
    assert 'c' == view[2]
    assert 'a' == view[-3]
    assert 'b' == view[-2]
    assert 'c' == view[-1]
    with raises(IndexError):
        view[3]
    with raises(IndexError):
        view[-4]


@tests.test
def slice():
    session = get_session()
    list_ = session.set(key('test_list_slice'), 'abcdefg', List)
    assert ['a'] == list(list_[:1])
    assert ['a', 'b', 'c', 'd'] == list(list_[:-3])
    assert ['a', 'b'] == list(list_[:2])
    assert ['a', 'c'] == list(list_[:3:2])
    assert ['d', 'e'] == list(list_[3:5])
    assert ['d', 'f'] == list(list_[3:6:2])
    assert ['d', 'e', 'f', 'g'] == list(list_[3:])
    assert ['e', 'f', 'g'] == list(list_[-3:])
    assert ['a', 'b', 'c', 'd', 'e', 'f', 'g'] == list(list_[:])


@tests.test
def set():
    session = get_session()
    list_ = session.set(key('test_list_set'), 'abc', List)
    list_[1] = 'B'
    assert ['a', 'B', 'c'] == list(list_)
    with raises(IndexError):
        list_[3] = 'D'


@tests.test
def set_slice():
    session = get_session()
    list_ = session.set(key('test_list_set_slice'), 'abc', List)
    list_[:0] = ['-2', '-1']
    assert ['-2', '-1', 'a', 'b', 'c'] == list(list_)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        list_[3:] = list('BC')
        assert len(w) == 1
        assert issubclass(w[0].category, PerformanceWarning)
    assert ['-2', '-1', 'a', 'B', 'C'] == list(list_)


@tests.test
def delete():
    session = get_session()
    list_ = session.set(key('test_list_delete'), 'abcdefg', List)
    del list_[0]
    assert list('bcdefg') == list(list_)
    del list_[-1]
    assert list('bcdef') == list(list_)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        del list_[2]
        assert len(w) == 1
        assert issubclass(w[0].category, PerformanceWarning)
    assert list('bcef') == list(list_)
    del list_[:]
    with raises(IndexError):
        del list_[-1]
    with raises(IndexError):
        del list_[0]


@tests.test
def delete_slice():
    session = get_session()
    list_ = session.set(key('test_list_delete_slice'), 'abcdefg', List)
    del list_[:2]
    assert list('cdefg') == list(list_)
    del list_[3:]
    assert list('cde') == list(list_)
    del list_[:]
    assert 0 == len(list_)
    list_ = session.set(key('test_list_delete_slice2'), 'abcdefg', List)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        del list_[2:5]
        assert len(w) == 1
        assert issubclass(w[0].category, PerformanceWarning)
    assert list('abfg') == list(list_)


@tests.test
def append():
    session = get_session()
    list_ = session.set(key('test_list_append'), 'abcd', List)
    list_.append('e')
    assert ['a', 'b', 'c', 'd', 'e'] == list(list_)
    list_.append('f')
    assert ['a', 'b', 'c', 'd', 'e', 'f'] == list(list_)


@tests.test
def extend():
    session = get_session()
    list_ = session.set(key('test_list_extend'), 'ab', List)
    list_.extend('cde')
    assert ['a', 'b', 'c', 'd', 'e'] == list(list_)
    list_.extend(['fg', 'hi'])
    assert ['a', 'b', 'c', 'd', 'e', 'fg', 'hi'] == list(list_)


@tests.test
def insert():
    session = get_session()
    list_ = session.set(key('test_list_insert'), ['b'], List)
    list_.insert(0, 'a')
    assert ['a', 'b'] == list(list_)
    list_.insert(-1, 'c')
    assert ['a', 'b', 'c'] == list(list_)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        list_.insert(1, 'a-b')
        assert len(w) == 1
        assert issubclass(w[0].category, PerformanceWarning)
    assert ['a', 'a-b', 'b', 'c'] == list(list_)


@tests.test
def pop():
    session = get_session()
    list_ = session.set(key('test_list_pop'), 'abcdefg', List)
    popped = list_.pop(0)
    assert 'a' == popped
    assert list('bcdefg') == list(list_)
    popped = list_.pop(-1)
    assert 'g' == popped
    assert list('bcdef') == list(list_)
    popped = list_.pop(2)
    assert 'd' == popped
    assert list('bcef') == list(list_)
    with raises(IndexError):
        list_.pop(10)
    with raises(IndexError):
        list_.pop(-10)
    del list_[:]
    with raises(IndexError):
        list_.pop(0)
    with raises(IndexError):
        list_.pop(-1)

