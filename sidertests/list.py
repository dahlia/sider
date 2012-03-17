import warnings
from attest import Tests, assert_hook, raises
from .env import get_session, key
from sider.list import PerformanceWarning


tests = Tests()


@tests.test
def iterate():
    session = get_session()
    session[key('test_list_iterate')] = ['a', 'b', 'c']
    assert ['a', 'b', 'c'] == list(session[key('test_list_iterate')])


@tests.test
def length():
    session = get_session()
    session[key('test_list_length')] = ['a', 'b', 'c']
    assert len(session[key('test_list_length')]) == 3


@tests.test
def get():
    session = get_session()
    session[key('test_list_get')] = ['a', 'b', 'c']
    assert 'a' == session[key('test_list_get')][0]
    assert 'b' == session[key('test_list_get')][1]
    assert 'c' == session[key('test_list_get')][2]
    assert 'a' == session[key('test_list_get')][-3]
    assert 'b' == session[key('test_list_get')][-2]
    assert 'c' == session[key('test_list_get')][-1]
    with raises(IndexError):
        session[key('test_list_get')][3]
    with raises(IndexError):
        session[key('test_list_get')][-4]


@tests.test
def slice():
    session = get_session()
    session[key('test_list_slice')] = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    list_ = session[key('test_list_slice')]
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
    session[key('test_list_set')] = ['a', 'b', 'c']
    list_ = session[key('test_list_set')]
    list_[1] = 'B'
    assert ['a', 'B', 'c'] == list(list_)
    with raises(IndexError):
        list_[3] = 'D'


@tests.test
def set_slice():
    session = get_session()
    session[key('test_list_set_slice')] = ['a', 'b', 'c']
    list_ = session[key('test_list_set_slice')]
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
    session[key('test_list_delete')] = list('abcdefg')
    list_ = session[key('test_list_delete')]
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
    session[key('test_list_delete_slice')] = list('abcdefg')
    list_ = session[key('test_list_delete_slice')]
    del list_[:2]
    assert list('cdefg') == list(list_)
    del list_[3:]
    assert list('cde') == list(list_)
    del list_[:]
    assert 0 == len(list_)
    session[key('test_list_delete_slice2')] = list('abcdefg')
    list_ = session[key('test_list_delete_slice2')]
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        del list_[2:5]
        assert len(w) == 1
        assert issubclass(w[0].category, PerformanceWarning)
    assert list('abfg') == list(list_)


@tests.test
def append():
    session = get_session()
    session[key('test_list_append')] = ['a', 'b', 'c', 'd']
    list_ = session[key('test_list_append')]
    list_.append('e')
    assert ['a', 'b', 'c', 'd', 'e'] == list(list_)
    list_.append('f')
    assert ['a', 'b', 'c', 'd', 'e', 'f'] == list(list_)


@tests.test
def extend():
    session = get_session()
    session[key('test_list_extend')] = ['a', 'b']
    list_ = session[key('test_list_extend')]
    list_.extend('cde')
    assert ['a', 'b', 'c', 'd', 'e'] == list(list_)
    list_.extend(['fg', 'hi'])
    assert ['a', 'b', 'c', 'd', 'e', 'fg', 'hi'] == list(list_)


@tests.test
def insert():
    session = get_session()
    session[key('test_list_insert')] = ['b']
    list_ = session[key('test_list_insert')]
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
    session[key('test_list_pop')] = list('abcdefg')
    list_ = session[key('test_list_pop')]
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

