from attest import Tests, assert_hook, raises
from .env import get_session, key
from sider.types import Set, Integer


tests = Tests()

S = frozenset
IntSet = Set(Integer)


@tests.test
def iterate():
    session = get_session()
    set_ = session.set(key('test_set_iterate'), S('abc'), Set)
    assert S(['a', 'b', 'c']) == S(set_)
    setx = session.set(key('test_setx_iterate'), S([1, 2, 3]), Set(Integer))
    assert S([1, 2, 3]) == S(setx)


@tests.test
def length():
    session = get_session()
    set_ = session.set(key('test_set_length'), S('abc'), Set)
    assert len(set_) == 3
    setx = session.set(key('test_setx_length'), S([1, 2, 3]), Set(Integer))
    assert len(setx) == 3


@tests.test
def contains():
    session = get_session()
    set_ = session.set(key('test_set_contains'), S('abc'), Set)
    assert 'a' in set_
    assert 'd' not in set_
    setx = session.set(key('test_setx_contains'), S([1, 2, 3]), Set(Integer))
    assert 1 in setx
    assert 4 not in setx
    assert '1' not in setx
    assert '4' not in setx


@tests.test
def equals():
    session = get_session()
    set_ = session.set(key('test_set_equals'), S('abc'), Set)
    assert set_ == set('abc')
    assert set_ == S('abc')


@tests.test
def isdisjoint():
    session = get_session()
    set_ = session.set(key('test_set_isdisjoint'), S('abc'), Set)
    setj = session.set(key('test_set_isdisjoint2'), S('cde'), Set)
    setd = session.set(key('test_set_isdisjoint3'), S('def1'), Set)
    assert not set_.isdisjoint('cde')
    assert set_.isdisjoint('def')
    assert not set_.isdisjoint(S('cde'))
    assert set_.isdisjoint(S('def'))
    assert not set_.isdisjoint(setj)
    assert set_.isdisjoint(setd)
    assert not setj.isdisjoint(set_)
    assert setd.isdisjoint(set_)
    setx = session.set(key('test_setx_isdisjoint'), S([1, 2, 3]), IntSet)
    setxj = session.set(key('test_setx_isdisjoint2'), S([3, 4, 5]), IntSet)
    setxd = session.set(key('test_setx_isdisjoint3'), S([4, 5, 6]), IntSet)
    assert not setx.isdisjoint([3, 4, 5])
    assert setx.isdisjoint([4, 5, 6])
    assert not setx.isdisjoint(S([3, 4, 5]))
    assert setx.isdisjoint(S([4, 5, 6]))
    assert not setx.isdisjoint(setxj)
    assert setx.isdisjoint(setxd)
    assert not setxj.isdisjoint(setx)
    assert setxd.isdisjoint(setx)
    # mismatched value_type Integer vs. Bulk:
    assert setd.isdisjoint(setx)
    assert setx.isdisjoint(setd)
    assert setd.isdisjoint(setxj)
    assert setd.isdisjoint(setxd)
    assert setxj.isdisjoint(setd)
    assert setxd.isdisjoint(setd)


@tests.test
def difference():
    session = get_session()
    set_ = session.set(key('test_set_difference'), S('abcd'), Set)
    set2 = session.set(key('test_set_difference2'), S('bde1'), Set)
    assert set_.difference(set2) == S('ac')
    assert set_.difference('bdef') == S('ac')
    assert set_.difference(S('bdef')) == S('ac')
    assert set_ - set2 == S('ac')
    assert set_ - S('bdef') == S('ac')
    with raises(TypeError):
        set_ - 'bdef'
    setx = session.set(key('test_setx_difference'), S([1, 2, 3, 4]), IntSet)
    sety = session.set(key('test_setx_difference2'), S([2, 4, 5, 6]), IntSet)
    assert setx.difference(sety) == S([1, 3])
    assert setx.difference([2, 4, 5, 6]) == S([1, 3])
    assert setx.difference(S([2, 4, 5, 6])) == S([1, 3])
    assert setx - sety == S([1, 3])
    assert setx - S([2, 4, 5, 6]) == S([1, 3])
    with raises(TypeError):
        setx - [2, 4, 5, 6]
    # mismatched value_type Integer vs. Bulk:
    assert set2 == set2.difference(setx)
    assert setx == setx.difference(set2)


@tests.test
def union():
    session = get_session()
    set_ = session.set(key('test_set_union'), S('abc'), Set)
    set2 = session.set(key('test_set_union2'), S('cde'), Set)
    set3 = session.set(key('test_set_union3'), S('def'), Set)
    assert set_.union('cde') == S('abcde')
    assert set_.union('cde', 'def') == S('abcdef')
    assert set_.union(S('cde')) == S('abcde')
    assert set_.union(S('cde'), 'def') == S('abcdef')
    assert set_.union(S('cde'), S('def')) == S('abcdef')
    assert set_.union(set2) == S('abcde')
    assert set_.union(set2, set3) == S('abcdef')
    assert set_.union(set2, set3, 'adfg') == S('abcdefg')
    assert set_ | S('cde') == S('abcde')
    assert set_ | set2 == S('abcde')
    with raises(TypeError):
        set_ | 'cde'
    setx = session.set(key('test_setx_union'), S([1, 2, 3]), IntSet)
    sety = session.set(key('test_setx_union2'), S([3, 4, 5]), IntSet)
    setz = session.set(key('test_setx_union3'), S([4, 5, 6]), IntSet)
    assert setx.union([3, 4, 5]) == S([1, 2, 3, 4, 5])
    assert setx.union([3, 4, 5], [4, 5, 6]) == S([1, 2, 3, 4, 5, 6])
    assert setx.union(S([3, 4, 5])) == S([1, 2, 3, 4, 5])
    assert setx.union(S([3, 4, 5]), [4, 5, 6]) == S([1, 2, 3, 4, 5, 6])
    assert setx.union(S([3, 4, 5]), S([4, 5, 6])) == S([1, 2, 3, 4, 5, 6])
    assert setx.union(sety) == S([1, 2, 3, 4, 5])
    assert setx.union(sety, setz) == S([1, 2, 3, 4, 5, 6])
    assert setx.union(sety, setz, [1, 4, 6, 7]) == S([1, 2, 3, 4, 5, 6, 7])
    assert setx | S([3, 4, 5]) == S([1, 2, 3, 4, 5])
    assert setx | sety == S([1, 2, 3, 4, 5])
    with raises(TypeError):
        setx | [3, 4, 5]
    assert set_.union(setx) == S(['a', 'b', 'c', 1, 2, 3])
    assert set_.union(setx, sety) == S(['a', 'b', 'c', 1, 2, 3, 4, 5])
    assert (set_.union(set2, setx, sety)
            == S(['a', 'b', 'c', 'd', 'e', 1, 2, 3, 4, 5]))
    assert set_ | setx == S(['a', 'b', 'c', 1, 2, 3])


'''
import warnings
from sider.warnings import PerformanceWarning


@tests.test
def length():
    session = get_session()
    view = session.set(key('test_list_length'), 'abc', List)
    assert len(view) == 3
    viewx = session.set(key('test_listx_length'), [1, 2, 3], List(Integer))
    assert len(viewx) == 3


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
    viewx = session.set(key('test_listx_get'), [1, 2, 3], List(Integer))
    assert 1 == viewx[0]
    assert 2 == viewx[1]
    assert 3 == viewx[2]
    assert 1 == viewx[-3]
    assert 2 == viewx[-2]
    assert 3 == viewx[-1]
    with raises(IndexError):
        viewx[3]
    with raises(IndexError):
        viewx[-4]


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
    listx = session.set(key('test_listx_slice'), range(1, 8), List(Integer))
    assert [1] == list(listx[:1])
    assert [1, 2, 3, 4] == list(listx[:-3])
    assert [1, 2] == list(listx[:2])
    assert [1, 3] == list(listx[:3:2])
    assert [4, 5] == list(listx[3:5])
    assert [4, 6] == list(listx[3:6:2])
    assert [4, 5, 6, 7] == list(listx[3:])
    assert [5, 6, 7] == list(listx[-3:])
    assert [1, 2, 3, 4, 5, 6, 7] == list(listx[:])


@tests.test
def set():
    session = get_session()
    list_ = session.set(key('test_list_set'), 'abc', List)
    list_[1] = 'B'
    with raises(TypeError):
        list_[2] = 3
    assert ['a', 'B', 'c'] == list(list_)
    with raises(IndexError):
        list_[3] = 'D'
    listx = session.set(key('test_listx_set'), [1, 2, 3], List(Integer))
    listx[1] = -2
    with raises(TypeError):
        listx[2] = 'c'
    assert [1, -2, 3] == list(listx)
    with raises(IndexError):
        listx[3] = 4


@tests.test
def set_slice():
    session = get_session()
    list_ = session.set(key('test_list_set_slice'), 'abc', List)
    list_[:0] = ['-2', '-1']
    with raises(TypeError):
        list_[:] = [object(), object()]
    with raises(TypeError):
        list_[0:] = [object(), object()]
    with raises(TypeError):
        list_[:0] = [object(), object()]
    with raises(TypeError):
        list_[1:2] = [object(), object()]
    assert ['-2', '-1', 'a', 'b', 'c'] == list(list_)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        list_[3:] = list('BC')
        assert len(w) == 1
        assert issubclass(w[0].category, PerformanceWarning)
    assert ['-2', '-1', 'a', 'B', 'C'] == list(list_)
    listx = session.set(key('test_listx_set_slice'), [1, 2, 3], List(Integer))
    listx[:0] = [-2, -1]
    with raises(TypeError):
        list_[:] = [object(), object()]
    with raises(TypeError):
        list_[0:] = [object(), object()]
    with raises(TypeError):
        list_[:0] = [object(), object()]
    with raises(TypeError):
        list_[1:2] = [object(), object()]
    assert [-2, -1, 1, 2, 3] == list(listx)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        listx[3:] = [-2, -3]
        assert len(w) == 1
        assert issubclass(w[0].category, PerformanceWarning)
    assert [-2, -1, 1, -2, -3] == list(listx)


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
    listx = session.set(key('test_listx_delete'), range(1, 8), List(Integer))
    del listx[0]
    assert range(2, 8) == list(listx)
    del listx[-1]
    assert range(2, 7) == list(listx)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        del listx[2]
        assert len(w) == 1
        assert issubclass(w[0].category, PerformanceWarning)
    assert [2, 3, 5, 6] == list(listx)
    del listx[:]
    with raises(IndexError):
        del listx[-1]
    with raises(IndexError):
        del listx[0]


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
    listx = session.set(key('test_listx_delete_slice'), range(1, 8),
                        value_type=List(Integer))
    del listx[:2]
    assert range(3, 8) == list(listx)
    del listx[3:]
    assert [3, 4, 5] == list(listx)
    del listx[:]
    assert 0 == len(listx)
    listx = session.set(key('test_listx_delete_slice2'), range(1, 8),
                        value_type=List(Integer))
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        del listx[2:5]
        assert len(w) == 1
        assert issubclass(w[0].category, PerformanceWarning)
    assert [1, 2, 6, 7] == list(listx)


@tests.test
def append():
    session = get_session()
    list_ = session.set(key('test_list_append'), 'abcd', List)
    list_.append('e')
    assert ['a', 'b', 'c', 'd', 'e'] == list(list_)
    list_.append('f')
    assert ['a', 'b', 'c', 'd', 'e', 'f'] == list(list_)
    with raises(TypeError):
        list_.append(123)
    listx = session.set(key('test_listx_append'), range(1, 5), List(Integer))
    listx.append(5)
    assert range(1, 6) == list(listx)
    listx.append(6)
    assert range(1, 7) == list(listx)
    with raises(TypeError):
        listx.append('abc')


@tests.test
def extend():
    session = get_session()
    list_ = session.set(key('test_list_extend'), 'ab', List)
    list_.extend('cde')
    assert ['a', 'b', 'c', 'd', 'e'] == list(list_)
    list_.extend(['fg', 'hi'])
    assert ['a', 'b', 'c', 'd', 'e', 'fg', 'hi'] == list(list_)
    with raises(TypeError):
        list_.extend([object(), object()])
    listx = session.set(key('test_listx_extend'), [1, 2], List(Integer))
    listx.extend([3, 4, 5])
    assert range(1, 6) == list(listx)
    listx.extend([67, 89])
    assert [1, 2, 3, 4, 5, 67, 89] == list(listx)
    with raises(TypeError):
        listx.extend([object(), object()])


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
    with raises(TypeError):
        list_.insert(0, object())
    with raises(TypeError):
        list_.insert(-1, object())
    with raises(TypeError):
        list_.insert(1, object())
    session = get_session()
    listx = session.set(key('test_listx_insert'), [2], List(Integer))
    listx.insert(0, 1)
    assert [1, 2] == list(listx)
    listx.insert(-1, 3)
    assert [1, 2, 3] == list(listx)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        listx.insert(1, 12)
        assert len(w) == 1
        assert issubclass(w[0].category, PerformanceWarning)
    assert [1, 12, 2, 3] == list(listx)
    with raises(TypeError):
        listx.insert(0, object())
    with raises(TypeError):
        listx.insert(-1, object())
    with raises(TypeError):
        listx.insert(1, object())


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
    listx = session.set(key('test_listx_pop'), range(1, 8), List(Integer))
    popped = listx.pop(0)
    assert 1 == popped
    assert range(2, 8) == list(listx)
    popped = listx.pop(-1)
    assert 7 == popped
    assert range(2, 7) == list(listx)
    popped = listx.pop(2)
    assert 4 == popped
    assert [2, 3, 5, 6] == list(listx)
    with raises(IndexError):
        listx.pop(10)
    with raises(IndexError):
        listx.pop(-10)
    del listx[:]
    with raises(IndexError):
        listx.pop(0)
    with raises(IndexError):
        listx.pop(-1)
#'''
