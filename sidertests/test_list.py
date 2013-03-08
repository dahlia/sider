import warnings
from pytest import raises
from .env import NInt, get_session, key
from .env import session
from sider.types import List
from sider.transaction import Transaction
from sider.exceptions import CommitError
from sider.warnings import PerformanceWarning


def test_iterate(session):
    view = session.set(key('test_list_iterate'), 'abc', List)
    assert ['a', 'b', 'c'] == list(view)
    view = session.set(key('test_listx_iterate'), [1, 2, 3], List(NInt))
    assert [1, 2, 3] == list(view)


def test_length(session):
    view = session.set(key('test_list_length'), 'abc', List)
    assert len(view) == 3
    viewx = session.set(key('test_listx_length'), [1, 2, 3], List(NInt))
    assert len(viewx) == 3


def test_get(session):
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
    viewx = session.set(key('test_listx_get'), [1, 2, 3], List(NInt))
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


def test_slice(session):
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
    listx = session.set(key('test_listx_slice'), range(1, 8), List(NInt))
    assert [1] == list(listx[:1])
    assert [1, 2, 3, 4] == list(listx[:-3])
    assert [1, 2] == list(listx[:2])
    assert [1, 3] == list(listx[:3:2])
    assert [4, 5] == list(listx[3:5])
    assert [4, 6] == list(listx[3:6:2])
    assert [4, 5, 6, 7] == list(listx[3:])
    assert [5, 6, 7] == list(listx[-3:])
    assert [1, 2, 3, 4, 5, 6, 7] == list(listx[:])


def test_set(session):
    list_ = session.set(key('test_list_set'), 'abc', List)
    list_[1] = 'B'
    with raises(TypeError):
        list_[2] = 3
    assert ['a', 'B', 'c'] == list(list_)
    with raises(IndexError):
        list_[3] = 'D'
    listx = session.set(key('test_listx_set'), [1, 2, 3], List(NInt))
    listx[1] = -2
    with raises(TypeError):
        listx[2] = 'c'
    assert [1, -2, 3] == list(listx)
    with raises(IndexError):
        listx[3] = 4


def test_set_t(session):
    session2 = get_session()
    keyid = key('test_list_set_t')
    list_ = session.set(keyid, 'abc', List)
    list2 = session2.get(keyid, List)
    with Transaction(session, [keyid]):
        size = len(list_)
        assert size == 3
        list_[1] = 'B'
        assert list2[:] == list('abc')
    assert list_[:] == list2[:] == list('aBc')
    with Transaction(session, [keyid]):
        with raises(IndexError):
            list_[3] = 'D'


def test_set_slice(session):
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
        assert len(w) == 1, 'no warning'
        assert issubclass(w[0].category, PerformanceWarning)
    assert ['-2', '-1', 'a', 'B', 'C'] == list(list_)
    listx = session.set(key('test_listx_set_slice'), [1, 2, 3], List(NInt))
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


def test_set_slice_t(session):
    session2 = get_session()
    keyid = key('test_list_set_slice_t')
    list_ = session.set(keyid, 'abc', List)
    list2 = session2.get(keyid, List)
    with Transaction(session, [keyid]):
        size = len(list_)
        assert size == 3
        list_[:0] = ['-2', '-1']
        assert list2[:] == list('abc')
    assert list_[:] == list2[:] == ['-2', '-1', 'a', 'b', 'c']
    with Transaction(session, [keyid]):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            list_[3:] = list('BC')
            assert len(w) == 1, 'no warning'
            assert issubclass(w[0].category, PerformanceWarning)
        assert list2[:] == ['-2', '-1', 'a', 'b', 'c']
    assert list_[:] == ['-2', '-1', 'a', 'B', 'C']


def test_delete(session):
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
    listx = session.set(key('test_listx_delete'), range(1, 8), List(NInt))
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


def test_delete_t(session):
    session2 = get_session()
    keyid = key('test_list_delete_t')
    list_ = session.set(keyid, 'abcdefg', List)
    list2 = session2.get(keyid, List)
    with Transaction(session, [keyid]):
        size = len(list_)
        assert size == 7
        del list_[0]
        assert list2[:] == list('abcdefg')
    assert list_[:] == list2[:] == list('bcdefg')
    with Transaction(session, [keyid]):
        size = len(list_)
        assert size == 6
        del list_[-1]
        assert list2[:] == list('bcdefg')
    assert list_[:] == list2[:] == list('bcdef')
    with Transaction(session, [keyid]):
        size = len(list_)
        assert size == 5
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            del list_[2]
            assert len(w) == 1
            assert issubclass(w[0].category, PerformanceWarning)
        assert list2[:] == list('bcdef')
    assert list_[:] == list2[:] == list('bcef')
    with Transaction(session, [keyid]):
        size = len(list_)
        assert size == 4
        del list_[:]
        assert list2[:] == list('bcef')
    assert len(list_[:]) == len(list2[:]) == 0
    with Transaction(session, [keyid]):
        with raises(IndexError):
            del list_[-1]
    with Transaction(session, [keyid]):
        with raises(IndexError):
            del list_[0]


def test_delete_slice(session):
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
                        value_type=List(NInt))
    del listx[:2]
    assert range(3, 8) == list(listx)
    del listx[3:]
    assert [3, 4, 5] == list(listx)
    del listx[:]
    assert 0 == len(listx)
    listx = session.set(key('test_listx_delete_slice2'), range(1, 8),
                        value_type=List(NInt))
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        del listx[2:5]
        assert len(w) == 1
        assert issubclass(w[0].category, PerformanceWarning)
    assert [1, 2, 6, 7] == list(listx)


def test_delete_slice_t(session):
    session2 = get_session()
    keyid = key('test_list_delete_slice_t')
    list_ = session.set(keyid, 'abcdefg', List)
    list2 = session2.get(keyid, List)
    with Transaction(session, [keyid]):
        size = len(list_)
        assert size == 7
        del list_[:2]
        assert list2[:] == list('abcdefg')
    assert list_[:] == list2[:] == list('cdefg')
    with Transaction(session, [keyid]):
        size = len(list_)
        assert size == 5
        del list_[3:]
        assert list2[:] == list('cdefg')
    assert list_[:] == list2[:] == list('cde')
    with Transaction(session, [keyid]):
        size = len(list_)
        assert size == 3
        del list_[:]
        assert list2[:] == list('cde')
    assert len(list_) == len(list2) == 0
    keyid = key('test_list_delete_slice_t')
    list_ = session.set(keyid, 'abcdefg', List)
    list2 = session2.get(keyid, List)
    with Transaction(session, [keyid]):
        size = len(list_)
        assert size == 7
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            del list_[2:5]
            assert len(w) == 1
            assert issubclass(w[0].category, PerformanceWarning)
        assert list2[:] == list('abcdefg')
    assert list_[:] == list2[:] == list('abfg')
    try:
        with Transaction(session, [keyid]):
            del list_[:]
            try:
                len(list_)
            except CommitError:
                raise
            else:
                assert False, 'expected CommitError'
    except CommitError:
        pass
    assert list_[:] == list2[:] == list('abfg')


def test_append(session):
    list_ = session.set(key('test_list_append'), 'abcd', List)
    list_.append('e')
    assert ['a', 'b', 'c', 'd', 'e'] == list(list_)
    list_.append('f')
    assert ['a', 'b', 'c', 'd', 'e', 'f'] == list(list_)
    with raises(TypeError):
        list_.append(123)
    listx = session.set(key('test_listx_append'), range(1, 5), List(NInt))
    listx.append(5)
    assert range(1, 6) == list(listx)
    listx.append(6)
    assert range(1, 7) == list(listx)
    with raises(TypeError):
        listx.append('abc')


def test_extend(session):
    list_ = session.set(key('test_list_extend'), 'ab', List)
    list_.extend('cde')
    assert ['a', 'b', 'c', 'd', 'e'] == list(list_)
    list_.extend(['fg', 'hi'])
    assert ['a', 'b', 'c', 'd', 'e', 'fg', 'hi'] == list(list_)
    with raises(TypeError):
        list_.extend([object(), object()])
    listx = session.set(key('test_listx_extend'), [1, 2], List(NInt))
    listx.extend([3, 4, 5])
    assert range(1, 6) == list(listx)
    listx.extend([67, 89])
    assert [1, 2, 3, 4, 5, 67, 89] == list(listx)
    with raises(TypeError):
        listx.extend([object(), object()])


def test_insert(session):
    list_ = session.set(key('test_list_insert'), ['b'], List)
    list_.insert(0, 'a')
    assert ['a', 'b'] == list(list_)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        list_.insert(-1, 'a-b')
        assert len(w) == 1
        assert issubclass(w[0].category, PerformanceWarning)
    assert ['a', 'a-b', 'b'] == list(list_)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        list_.insert(-2, 'a-a-b')
        assert len(w) == 1
        assert issubclass(w[0].category, PerformanceWarning)
    assert ['a', 'a-a-b', 'a-b', 'b'] == list(list_)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        list_.insert(1, 'a-a-a-b')
        assert len(w) == 1
        assert issubclass(w[0].category, PerformanceWarning)
    assert ['a', 'a-a-a-b', 'a-a-b', 'a-b', 'b'] == list(list_)
    with raises(TypeError):
        list_.insert(0, object())
    with raises(TypeError):
        list_.insert(-1, object())
    with raises(TypeError):
        list_.insert(1, object())
    listx = session.set(key('test_listx_insert'), [3], List(NInt))
    listx.insert(0, 1)
    assert [1, 3] == list(listx)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        listx.insert(-1, 2)
        assert len(w) == 1
        assert issubclass(w[0].category, PerformanceWarning)
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


def test_insert_t(session):
    keyid = key('test_list_insert_t')
    list_ = session.set(keyid, 'abcdefg', List)
    with Transaction(session, [keyid]):
        first = list_[0]
        assert first == 'a'
        list_.insert(0, 'Z')
    assert list_[:] == list('Zabcdefg')
    with Transaction(session, [keyid]):
        first = list_[0]
        assert first == 'Z'
        list_.insert(-1, 'G')
    assert list_[:] == list('ZabcdefGg')
    with Transaction(session, [keyid]):
        first = list_[0]
        assert first == 'Z'
        list_.insert(2, 'A')
    assert list_[:] == list('ZaAbcdefGg')
    with Transaction(session, [keyid]):
        first = list_[0]
        assert first == 'Z'
        list_.insert(-3, 'F')
    assert list_[:] == list('ZaAbcdeFfGg')


def test_pop(session):
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
    popped = list_.pop(-2)
    assert 'e' == popped
    assert list('bcf') == list(list_)
    with raises(IndexError):
        list_.pop(10)
    with raises(IndexError):
        list_.pop(-10)
    del list_[:]
    with raises(IndexError):
        list_.pop(0)
    with raises(IndexError):
        list_.pop(-1)
    listx = session.set(key('test_listx_pop'), range(1, 8), List(NInt))
    popped = listx.pop(0)
    assert 1 == popped
    assert range(2, 8) == list(listx)
    popped = listx.pop(-1)
    assert 7 == popped
    assert range(2, 7) == list(listx)
    popped = listx.pop(2)
    assert 4 == popped
    assert [2, 3, 5, 6] == list(listx)
    popped = listx.pop(-2)
    assert 5 == popped
    assert [2, 3, 6] == list(listx)
    with raises(IndexError):
        listx.pop(10)
    with raises(IndexError):
        listx.pop(-10)
    del listx[:]
    with raises(IndexError):
        listx.pop(0)
    with raises(IndexError):
        listx.pop(-1)


def test_pop_t(session):
    keyid = key('test_list_pop_t')
    list_ = session.set(keyid, 'abcdefg', List)
    with Transaction(session, [keyid]):
        first = list_[0]
        assert first == 'a'
        popped = list_.pop()
        assert popped == 'g'
        list_.append('h')
    assert list_[:] == list('abcdefh')
    with Transaction(session, [keyid]):
        last = list_[-1]
        assert last == 'h'
        popped = list_.pop(0)
        assert popped == 'a'
        list_.append('i')
    assert list_[:] == list('bcdefhi')
    with Transaction(session, [keyid]):
        last = list_[-1]
        assert last == 'i'
        popped = list_.pop(2)
        assert popped == 'd'
        list_.append('j')
    assert list_[:] == list('bcefhij')
    with Transaction(session, [keyid]):
        last = list_[-1]
        assert last == 'j'
        popped = list_.pop(-3)
        assert popped == 'h'
        list_.append('k')
    assert list_[:] == list('bcefijk')
    with Transaction(session, [keyid]):
        list_.pop()
        with raises(CommitError):
            len(list_)
    with Transaction(session, [keyid]):
        list_.pop(-1)
        with raises(CommitError):
            len(list_)
    with Transaction(session, [keyid]):
        list_.pop(2)
        with raises(CommitError):
            len(list_)
    with Transaction(session, [keyid]):
        list_.pop(-2)
        with raises(CommitError):
            len(list_)


def test_repr_(session):
    keyid = key('test_list_repr')
    list_ = session.set(keyid, [1, 2, 3], List(NInt))
    r = repr(list_)
    assert '<sider.list.List (' + repr(keyid) + ') [1, 2, 3]>' == r
    list_ = session.set(keyid, range(20), List(NInt))
    r = repr(list_)
    assert '<sider.list.List ({0!r}) {1!r}>'.format(keyid, range(20)) == r
    list_.append(50)
    r = repr(list_)
    expected = '<sider.list.List ({0!r}) {1}, ...]>'.format(keyid,
        repr(range(20))[:-1])
    assert expected == r
