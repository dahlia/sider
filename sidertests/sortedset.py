from attest import Tests, assert_hook, raises
from .env import NInt, init_session, key
from sider.types import SortedSet


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
def update(session):
    def reset():
        return session.set(key('test_sortedset_update'), S('abc'), SortedSet)
    set_ = reset()
    set_.update('cde')
    assert S(set_) == S('abcde')
    assert list(set_)[-1] == 'c'
    reset()
    set_.update({'a': 1, 'b': 2, 'd': 1, 'e': 1})
    assert S(set_) == S('abcde')
    assert list(set_)[-1] == 'b'
    reset()
    set_.update(a=1, b=2, d=1, e=1)
    assert S(set_) == S('abcde')
    assert list(set_)[-1] == 'b'
    reset()
    set_.update('cde', {'b': 2, 'd': 5}, c=2)
    assert S(set_) == S('abcde')
    assert list(set_)[-3:] == list('bcd')
    def reset2():
        return session.set(key('test_sortedsetx_update'), S([1, 2, 3]), IntSet)
    setx = reset2()
    setx.update([3, 4, 5])
    assert S(setx) == S([1, 2, 3, 4, 5])
    assert list(setx)[-1] == 3
    reset2()
    setx.update({1: 1, 2: 2, 4: 1, 5: 1})
    assert S(setx) == S([1, 2, 3, 4, 5])
    assert list(setx)[-1] == 2
    reset2()
    setx.update([3, 4, 5], {2: 2, 4: 5, 3: 2})
    assert S(setx) == S([1, 2, 3, 4, 5])
    assert list(setx)[-3:] == [2, 3, 4]


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

