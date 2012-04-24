from attest import Tests, assert_hook, raises
from .env import NInt, get_session, init_session, key
from sider.types import SortedSet
from sider.transaction import Transaction
from sider.exceptions import CommitError


tests = Tests()
tests.context(init_session)

S = frozenset
IntSet = SortedSet(NInt)


@tests.test
def iterate(session):
    set_ = session.set(key('test_sortedset_iterate'),
                       {'a': 3, 'b': 1, 'c': 2},
                       SortedSet)
    assert list(set_) == ['b', 'c', 'a']
    setx = session.set(key('test_sortedsetx_iterate'),
                       {1: 3, 2: 1, 3: 2},
                       IntSet)
    assert list(setx) == [2, 3, 1]


@tests.test
def length(session):
    set_ = session.set(key('test_sortedset_length'), S('abc'), SortedSet)
    assert len(set_) == 3
    setx = session.set(key('test_sortedsetx_length'), S([1, 2, 3]), IntSet)
    assert len(setx) == 3


@tests.test
def contains(session):
    set_ = session.set(key('test_sortedset_contains'), S('abc'), SortedSet)
    assert 'a' in set_
    assert 'd' not in set_
    setx = session.set(key('test_sortedsetx_contains'), S([1, 2, 3]), IntSet)
    assert 1 in setx
    assert 4 not in setx
    assert '1' not in setx
    assert '4' not in setx


@tests.test
def getitem(session):
    set_ = session.set(key('test_sortedset_getitem'), S('abc'), SortedSet)
    assert set_['a'] == 1
    assert set_['b'] == 1
    assert set_['c'] == 1
    with raises(KeyError):
        set_['d']
    with raises(TypeError):
        set_[123]
    set_.update(a=2.1, c=-2)
    assert set_['a'] == 3.1
    assert set_['b'] == 1
    assert set_['c'] == -1
    setx = session.set(key('test_sortedsetx_getitem'), S([1, 2, 3]), IntSet)
    assert setx[1] == 1
    assert setx[2] == 1
    assert setx[3] == 1
    with raises(KeyError):
        setx[4]
    with raises(TypeError):
        setx['a']
    setx.update({1: 2.1, 3: -2})
    assert setx[1] == 3.1
    assert setx[2] == 1
    assert setx[3] == -1


@tests.test
def setitem(session):
    set_ = session.set(key('test_sortedset_setitem'), S('abc'), SortedSet)
    set_['d'] = 1
    set_['a'] = 2.1
    assert dict(set_) == {'a': 2.1, 'b': 1, 'c': 1, 'd': 1}
    with raises(TypeError):
        set_[123] = 123
    with raises(TypeError):
        set_['a'] = 'a'
    setx = session.set(key('test_sortedsetx_setitem'), S([1, 2, 3]), IntSet)
    setx[4] = 1
    setx[1] = 2.1
    assert dict(setx) == {1: 2.1, 2: 1, 3: 1, 4: 1}
    with raises(TypeError):
        setx['a'] = 123
    with raises(TypeError):
        setx[123] = 'a'


@tests.test
def delitem(session):
    set_ = session.set(key('test_sortedset_delitem'), S('abc'), SortedSet)
    del set_['b']
    assert S(set_) == S('ac')
    with raises(KeyError):
        del set_['d']
    with raises(TypeError):
        del set_[123]
    setx = session.set(key('test_sortedsetx_delitem'), S([1, 2, 3]), IntSet)
    del setx[2]
    assert S(setx) == S([1, 3])
    with raises(KeyError):
        del setx[4]
    with raises(TypeError):
        del setx['a']


@tests.test
def delitem_t(session):
    session2 = get_session()
    keyid = key('test_sortedset_delitem_t')
    set_ = session.set(keyid, S('abc'), SortedSet)
    set2 = session2.get(keyid, SortedSet)
    with Transaction(session, [keyid]):
        card = len(set_)
        assert card == 3
        del set_['b']
        assert S(set2) == S('abc')
        with raises(CommitError):
            len(set_)
    assert S(set_) == S(set2) == S('ac')
    with Transaction(session, [keyid]):
        with raises(KeyError):
            del set_['d']
    with Transaction(session, [keyid]):
        with raises(TypeError):
            del set_[123]
    keyid2 = key('test_sortedsetx_delitem_t')
    setx = session.set(keyid2, S([1, 2, 3]), IntSet)
    sety = session2.get(keyid2, IntSet)
    with Transaction(session, [keyid]):
        card = len(setx)
        assert card == 3
        del setx[2]
        assert S(sety) == S([1, 2, 3])
        with raises(CommitError):
            len(setx)
    assert S(setx) == S(sety) == S([1, 3])
    with Transaction(session, [keyid]):
        with raises(KeyError):
            del setx[4]
    with Transaction(session, [keyid]):
        with raises(TypeError):
            del setx['a']


@tests.test
def keys(session):
    set_ = session.set(key('test_sortedset_keys'),
                       {'a': 3, 'b': 1, 'c': 2},
                       SortedSet)
    assert set_.keys() == S('abc')
    setx = session.set(key('test_sortedsetx_keys'), {1: 3, 2: 1, 3: 2}, IntSet)
    assert setx.keys() == S([1, 2, 3])


@tests.test
def items(session):
    set_ = session.set(key('test_sortedset_items'), S('abc'), SortedSet)
    assert set_.items() == S([('a', 1), ('b', 1), ('c', 1)])
    set_.update(b=1, c=2)
    assert set_.items() == S([('a', 1), ('b', 2), ('c', 3)])
    setx = session.set(key('test_sortedsetx_items'), S([1, 2, 3]), IntSet)
    assert setx.items() == S([(1, 1), (2, 1), (3, 1)])
    setx.update({2: 1, 3: 2})
    assert setx.items() == S([(1, 1), (2, 2), (3, 3)])


@tests.test
def values(session):
    set_ = session.set(key('test_sortedset_values'),
                       {'a': 3, 'b': 1, 'c': 2, 'd': 1},
                       SortedSet)
    assert set_.values() == [1, 1, 2, 3]
    setx = session.set(key('test_sortedsetx_values'),
                       {1: 3, 2: 1, 3: 2, 4: 1},
                       IntSet)
    assert setx.values() == [1, 1, 2, 3]


@tests.test
def equals(session):
    set_ = session.set(key('test_set_equals'), S('abc'), SortedSet)
    set2 = session.set(key('test_set_equals2'), S('abc'), SortedSet)
    set3 = session.set(key('test_set_equals3'), S('abcd'), SortedSet)
    set4 = session.set(key('test_set_equals3'), {'a': 1, 'b': 2, 'c': 1},
                       SortedSet)
    set5 = session.set(key('test_set_equals4'), S([1, 2, 3]), IntSet)
    emptyset = session.set(key('test_set_equals5'), S(), SortedSet)
    emptyset2 = session.set(key('test_set_equals5'), S(), IntSet)
    assert set_ == set('abc')
    assert set_ != set('abcd')
    assert set_ == {'a': 1, 'b': 1, 'c': 1}
    assert set_ != {'a': 1, 'b': 1, 'c': 1, 'd': 1}
    assert set_ != {'a': 1, 'b': 1, 'c': 2}
    assert set_ == S('abc')
    assert set_ != S('abcd')
    assert set_ == set2 and set2 == set_
    assert set_ != set3 and set3 != set_
    assert set_ != set4 and set4 != set_
    assert set_ != set5 and set5 != set_
    assert emptyset == emptyset2 and emptyset2 == emptyset


@tests.test
def add(session):
    set_ = session.set(key('test_sortedset_add'), S('abc'), SortedSet)
    set_.add('d')
    assert dict(set_) == {'a': 1, 'b': 1, 'c': 1, 'd': 1}
    set_.add('e', score=1.5)
    assert dict(set_) == {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1.5}
    set_.add('c')
    assert dict(set_) == {'a': 1, 'b': 1, 'c': 2, 'd': 1, 'e': 1.5}
    set_.add('c', score=1.5)
    assert dict(set_) == {'a': 1, 'b': 1, 'c': 3.5, 'd': 1, 'e': 1.5}
    with raises(TypeError):
        set_.add(123)
    with raises(TypeError):
        set_.add('a', score='1.5')
    setx = session.set(key('test_sortedsetx_add'), S([1, 2, 3]), IntSet)
    setx.add(4)
    assert dict(setx) == {1: 1, 2: 1, 3: 1, 4: 1}
    setx.add(5, score=1.5)
    assert dict(setx) == {1: 1, 2: 1, 3: 1, 4: 1, 5: 1.5}
    setx.add(3)
    assert dict(setx) == {1: 1, 2: 1, 3: 2, 4: 1, 5: 1.5}
    setx.add(3, score=1.5)
    assert dict(setx) == {1: 1, 2: 1, 3: 3.5, 4: 1, 5: 1.5}
    with raises(TypeError):
        setx.add('a')
    with raises(TypeError):
        setx.add(1, score='1.5')


@tests.test
def discard(session):
    set_ = session.set(key('test_sortedset_discard'), S('abc'), SortedSet)
    set_.discard('a')
    assert dict(set_) == {'b': 1, 'c': 1}
    set_.discard('d')
    assert dict(set_) == {'b': 1, 'c': 1}
    set_.discard('b', score=0.5)
    assert dict(set_) == {'b': 0.5, 'c': 1}
    set_.discard('b', score=0.5, remove=-1)
    assert dict(set_) == {'b': 0, 'c': 1}
    with raises(TypeError):
        set_.discard(123)
    with raises(TypeError):
        set_.discard('a', score='1.5')
    setx = session.set(key('test_sortedsetx_discard'), S([1, 2, 3]), IntSet)
    setx.discard(1)
    assert dict(setx) == {2: 1, 3: 1}
    setx.discard(4)
    assert dict(setx) == {2: 1, 3: 1}
    setx.discard(2, score=0.5)
    assert dict(setx) == {2: 0.5, 3: 1}
    setx.discard(2, score=0.5, remove=-1)
    assert dict(setx) == {2: 0, 3: 1}
    with raises(TypeError):
        setx.discard('a')
    with raises(TypeError):
        setx.discard(1, score='1.5')


@tests.test
def discard_t(session):
    session2 = get_session()
    keyid = key('test_sortedset_discard_t')
    set_ = session.set(keyid, S('abc'), SortedSet)
    set2 = session2.get(keyid, SortedSet)
    with Transaction(session, [keyid]):
        len(set_)
        set_.discard('a')
        assert dict(set2) == {'a': 1, 'b': 1, 'c': 1}
        with raises(CommitError):
            len(set_)
    assert dict(set_) == dict(set2) == {'b': 1, 'c': 1}
    with Transaction(session, [keyid]):
        len(set_)
        set_.discard('d')
        assert dict(set2) == {'b': 1, 'c': 1}
    assert dict(set_) == dict(set2) == {'b': 1, 'c': 1}
    with Transaction(session, [keyid]):
        len(set_)
        set_.discard('b', score=0.5)
        assert dict(set2) == {'b': 1, 'c': 1}
        with raises(CommitError):
            len(set_)
    assert dict(set_) == dict(set2) == {'b': 0.5, 'c': 1}
    with Transaction(session, [keyid]):
        len(set_)
        set_.discard('b', score=0.5, remove=-1)
        assert dict(set2) == {'b': 0.5, 'c': 1}
        with raises(CommitError):
            len(set_)
    assert dict(set_) == dict(set2) == {'b': 0, 'c': 1}


@tests.test
def clear(session):
    set_ = session.set(key('test_sortedset_clear'), S('abc'), SortedSet)
    set_.clear()
    assert len(set_) == 0
    setx = session.set(key('test_sortedsetx_clear'), S([1, 2, 3]), IntSet)
    setx.clear()
    assert len(setx) == 0


@tests.test
def update(session):
    def reset():
        return session.set(key('test_sortedset_update'), S('abc'), SortedSet)
    set_ = reset()
    set_.update('cde')
    assert dict(set_) == {'a': 1, 'b': 1, 'c': 2, 'd': 1, 'e': 1}
    reset()
    set_.update({'a': 1, 'b': 2, 'd': 1, 'e': 1.5})
    assert dict(set_) == {'a': 2, 'b': 3, 'c': 1, 'd': 1, 'e': 1.5}
    reset()
    set_.update(a=1, b=2, d=1, e=1.5)
    assert dict(set_) == {'a': 2, 'b': 3, 'c': 1, 'd': 1, 'e': 1.5}
    reset()
    set_.update('cde', {'b': 2, 'd': 5.1}, c=2.2)
    assert dict(set_) == {'a': 1, 'b': 3, 'c': 4.2, 'd': 6.1, 'e': 1}
    def reset2():
        return session.set(key('test_sortedsetx_update'), S([1, 2, 3]), IntSet)
    setx = reset2()
    setx.update([3, 4, 5])
    assert dict(setx) == {1: 1, 2: 1, 3: 2, 4: 1, 5: 1}
    reset2()
    setx.update({1: 1, 2: 2, 4: 1.5, 5: 1})
    assert dict(setx) == {1: 2, 2: 3, 3: 1, 4: 1.5, 5: 1}
    reset2()
    setx.update([3, 4, 5], {2: 2, 4: 5, 3: 2.1})
    assert dict(setx) == {1: 1, 2: 3, 3: 4.1, 4: 6, 5: 1}


@tests.test
def repr_(session):
    keyid = key('test_sortedset_repr')
    set_ = session.set(keyid, set([1, 2, 3]), IntSet)
    expected = '<sider.sortedset.SortedSet (' + repr(keyid) + ') {1, 2, 3}>'
    assert expected == repr(set_)
    set_.update({1: 1})
    expected = '<sider.sortedset.SortedSet (' + repr(keyid) + \
               ') {2, 3, 1: 2.0}>'
    assert expected == repr(set_)

