from pytest import raises
from .env import NInt, get_session, key
from .env import session
from sider.types import SortedSet
from sider.transaction import Transaction
from sider.exceptions import CommitError


S = frozenset
IntSet = SortedSet(NInt)


def test_iterate(session):
    set_ = session.set(key('test_sortedset_iterate'),
                       {'a': 3, 'b': 1, 'c': 2},
                       SortedSet)
    assert list(set_) == ['b', 'c', 'a']
    setx = session.set(key('test_sortedsetx_iterate'),
                       {1: 3, 2: 1, 3: 2},
                       IntSet)
    assert list(setx) == [2, 3, 1]


def test_length(session):
    set_ = session.set(key('test_sortedset_length'), S('abc'), SortedSet)
    assert len(set_) == 3
    setx = session.set(key('test_sortedsetx_length'), S([1, 2, 3]), IntSet)
    assert len(setx) == 3


def test_contains(session):
    set_ = session.set(key('test_sortedset_contains'), S('abc'), SortedSet)
    assert 'a' in set_
    assert 'd' not in set_
    setx = session.set(key('test_sortedsetx_contains'), S([1, 2, 3]), IntSet)
    assert 1 in setx
    assert 4 not in setx
    assert '1' not in setx
    assert '4' not in setx


def test_getitem(session):
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


def test_setitem(session):
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


def test_delitem(session):
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


def test_delitem_t(session):
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


def test_keys(session):
    set_ = session.set(key('test_sortedset_keys'),
                       {'a': 3, 'b': 1, 'c': 2},
                       SortedSet)
    assert list(set_.keys()) == ['b', 'c', 'a']
    assert list(set_.keys(reverse=True)) == ['a', 'c', 'b']
    setx = session.set(key('test_sortedsetx_keys'), {1: 3, 2: 1, 3: 2}, IntSet)
    assert list(setx.keys(reverse=True)) == [1, 3, 2]


def test_items(session):
    set_ = session.set(key('test_sortedset_items'),
                       {'a': 1, 'b': 2, 'c': 3},
                       SortedSet)
    assert set_.items() == [('a', 1), ('b', 2), ('c', 3)]
    assert set_.items(reverse=True) == [('c', 3), ('b', 2), ('a', 1)]
    setx = session.set(key('test_sortedsetx_items'),
                       {1: 1, 2: 2, 3: 3},
                       IntSet)
    assert setx.items() == [(1, 1), (2, 2), (3, 3)]
    assert setx.items(reverse=True) == [(3, 3), (2, 2), (1, 1)]


def test_values(session):
    set_ = session.set(key('test_sortedset_values'),
                       {'a': 3, 'b': 1, 'c': 2, 'd': 1},
                       SortedSet)
    assert set_.values() == [1, 1, 2, 3]
    assert set_.values(reverse=True) == [3, 2, 1, 1]
    setx = session.set(key('test_sortedsetx_values'),
                       {1: 3, 2: 1, 3: 2, 4: 1},
                       IntSet)
    assert setx.values() == [1, 1, 2, 3]
    assert setx.values(reverse=True) == [3, 2, 1, 1]


def test_most_common(session):
    set_ = session.set(key('test_sortedset_most_common'),
                       {'a': 5, 's': 4, 'd': 3, 'f': 2, 'g': 1},
                       SortedSet)
    assert set_.most_common(3) == [('a', 5), ('s', 4), ('d', 3)]
    assert set_.most_common() == [('a',5), ('s',4), ('d',3), ('f',2), ('g',1)]
    assert set_.most_common(3, reverse=True) == [('g', 1), ('f', 2), ('d', 3)]
    assert (set_.most_common(reverse=True) ==
            [('g', 1), ('f', 2), ('d', 3), ('s', 4), ('a', 5)])
    setx = session.set(key('test_sortedsetx_most_common'),
                       {7: 5, 3: 4, 9: 3, 2: 2, 6: 1},
                       IntSet)
    assert setx.most_common(3) == [(7, 5), (3, 4), (9, 3)]
    assert setx.most_common() == [(7, 5), (3, 4), (9, 3), (2, 2), (6, 1)]
    assert setx.most_common(3, reverse=True) == [(6, 1), (2, 2), (9, 3)]
    assert setx.most_common(reverse=True) == [(6, 1), (2, 2), (9, 3),
                                              (3, 4), (7, 5)]


def test_least_common(session):
    set_ = session.set(key('test_sortedset_least_common'),
                       {'a': 5, 's': 4, 'd': 3, 'f': 2, 'g': 1},
                       SortedSet)
    assert set_.least_common(3) == [('g', 1), ('f', 2), ('d', 3)]
    assert set_.least_common() == [('g',1), ('f',2), ('d',3), ('s',4), ('a',5)]
    assert set_.least_common(3, reverse=True) == [('a', 5), ('s', 4), ('d', 3)]
    assert (set_.least_common(reverse=True) ==
            [('a', 5), ('s', 4), ('d', 3), ('f', 2), ('g', 1)])
    setx = session.set(key('test_sortedsetx_least_common'),
                       {7: 5, 3: 4, 9: 3, 2: 2, 6: 1},
                       IntSet)
    assert setx.least_common(3) == [(6, 1), (2, 2), (9, 3)]
    assert setx.least_common() == [(6, 1), (2, 2), (9, 3), (3, 4), (7, 5)]
    assert setx.least_common(3, reverse=True) == [(7, 5), (3, 4), (9, 3)]
    assert setx.least_common(reverse=True) == [(7, 5), (3, 4), (9, 3),
                                               (2, 2), (6, 1)]


def test_equals(session):
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


def test_add(session):
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


def test_discard(session):
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


def test_discard_t(session):
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


def test_setdefault(session):
    set_ = session.set(key('test_sortedset_setdefault'),
                       {'h': 1, 'o': 2, 'n': 3, 'g': 4},
                       SortedSet)
    assert 1 == set_.setdefault('h')
    assert {'h': 1, 'o': 2, 'n': 3, 'g': 4} == dict(set_)
    assert 1 == set_.setdefault('h', 123)
    assert {'h': 1, 'o': 2, 'n': 3, 'g': 4} == dict(set_)
    assert 1 == set_.setdefault('m')
    assert {'h': 1, 'o': 2, 'n': 3, 'g': 4, 'm': 1} == dict(set_)
    assert 123 == set_.setdefault('i', 123)
    assert {'h': 1, 'o': 2, 'n': 3, 'g': 4, 'm': 1, 'i': 123} == dict(set_)
    with raises(TypeError):
        set_.setdefault('e', None)
    with raises(TypeError):
        set_.setdefault('e', '123')
    setx = session.set(key('test_sortedsetx_setdefault'),
                       {100: 1, 200: 2, 300: 3, 400: 4},
                       IntSet)
    assert 1 == setx.setdefault(100)
    assert {100: 1, 200: 2, 300: 3, 400: 4} == dict(setx)
    assert 1 == setx.setdefault(100, 123)
    assert {100: 1, 200: 2, 300: 3, 400: 4} == dict(setx)
    assert 1 == setx.setdefault(500)
    assert {100: 1, 200: 2, 300: 3, 400: 4, 500: 1} == dict(setx)
    assert 123 == setx.setdefault(600, 123)
    assert {100: 1, 200: 2, 300: 3, 400: 4, 500: 1, 600: 123} == dict(setx)
    with raises(TypeError):
        setx.setdefault(700, None)
    with raises(TypeError):
        setx.setdefault(700, '123')


def test_setdefault_t(session):
    session2 = get_session()
    keyid = key('test_sortedset_setdefault_t')
    set_ = session.set(keyid, {'h': 1, 'o': 2, 'n': 3, 'g': 4}, SortedSet)
    set2 = session2.get(keyid, SortedSet)
    with Transaction(session, [keyid]):
        len(set_)
        val = set_.setdefault('h')
        assert 1 == val
        assert {'h': 1, 'o': 2, 'n': 3, 'g': 4} == dict(set2)
    assert {'h': 1, 'o': 2, 'n': 3, 'g': 4} == dict(set_) == dict(set2)
    with Transaction(session, [keyid]):
        len(set_)
        val = set_.setdefault('h', 123)
        assert 1 == val
        assert {'h': 1, 'o': 2, 'n': 3, 'g': 4} == dict(set2)
    assert {'h': 1, 'o': 2, 'n': 3, 'g': 4} == dict(set_) == dict(set2)
    with Transaction(session, [keyid]):
        len(set_)
        val = set_.setdefault('m')
        assert 1 == val
        assert {'h': 1, 'o': 2, 'n': 3, 'g': 4} == dict(set2)
        with raises(CommitError):
            len(set_)
    assert {'h': 1, 'o': 2, 'n': 3, 'g': 4, 'm': 1} == dict(set_) == dict(set2)
    with Transaction(session, [keyid]):
        len(set_)
        val = set_.setdefault('i', 123)
        assert 123 == val
        assert {'h': 1, 'o': 2, 'n': 3, 'g': 4, 'm': 1} == dict(set2)
        with raises(CommitError):
            len(set_)
    assert ({'h': 1, 'o': 2, 'n': 3, 'g': 4, 'm': 1, 'i': 123}
            == dict(set_) == dict(set2))


def test_pop_set(session):
    set_ = session.set(key('test_sortedset_pop_set'),
                       {'h': 1, 'o': 2, 'n': 3, 'g': 4.5},
                       SortedSet)
    popped = set_.pop()
    assert popped == 'h'
    assert dict(set_) == {'o': 2, 'n': 3, 'g': 4.5}
    popped = set_.pop(desc=True)
    assert popped == 'g'
    assert dict(set_) == {'o': 2, 'n': 3, 'g': 3.5}
    popped = set_.pop(score=0.5)
    assert popped == 'o'
    assert dict(set_) == {'o': 1.5, 'n': 3, 'g': 3.5}
    popped = set_.pop(remove=0.5)
    assert popped == 'o'
    assert dict(set_) == {'n': 3, 'g': 3.5}
    popped = set_.pop(remove=None)
    assert popped == 'n'
    assert dict(set_) == {'g': 3.5}
    set_.clear()
    with raises(KeyError):
        set_.pop()
    setx = session.set(key('test_sortedsetx_pop_set'),
                       {3: 1, 1: 2, 4: 3, 5: 4.5},
                       IntSet)
    popped = setx.pop()
    assert popped == 3
    assert dict(setx) == {1: 2, 4: 3, 5: 4.5}
    popped = setx.pop(desc=True)
    assert popped == 5
    assert dict(setx) == {1: 2, 4: 3, 5: 3.5}
    popped = setx.pop(score=0.5)
    assert popped == 1
    assert dict(setx) == {1: 1.5, 4: 3, 5: 3.5}
    popped = setx.pop(remove=0.5)
    assert popped == 1
    assert dict(setx) == {4: 3, 5: 3.5}
    popped = setx.pop(remove=None)
    assert popped == 4
    assert dict(setx) == {5: 3.5}
    setx.clear()
    with raises(KeyError):
        setx.pop()


def test_pop_set_t(session):
    session2 = get_session()
    keyid = key('test_sortedset_pop_set_t')
    set_ = session.set(keyid, {'h': 1, 'o': 2, 'n': 3, 'g': 4.5}, SortedSet)
    set2 = session2.get(keyid, SortedSet)
    with Transaction(session, [keyid]):
        len(set_)
        popped = set_.pop()
        assert popped == 'h'
        assert dict(set2) == {'h': 1, 'o': 2, 'n': 3, 'g': 4.5}
        with raises(CommitError):
            len(set_)
    assert dict(set_) == dict(set2) == {'o': 2, 'n': 3, 'g': 4.5}
    with Transaction(session, [keyid]):
        len(set_)
        popped = set_.pop(desc=True)
        assert popped == 'g'
        assert dict(set2) == {'o': 2, 'n': 3, 'g': 4.5}
        with raises(CommitError):
            len(set_)
    assert dict(set_) == dict(set2) == {'o': 2, 'n': 3, 'g': 3.5}
    with Transaction(session, [keyid]):
        len(set_)
        popped = set_.pop(score=0.5)
        assert popped == 'o'
        assert dict(set2) == {'o': 2, 'n': 3, 'g': 3.5}
    assert dict(set_) == dict(set2) == {'o': 1.5, 'n': 3, 'g': 3.5}
    with Transaction(session, [keyid]):
        len(set_)
        popped = set_.pop(remove=0.5)
        assert popped == 'o'
        assert dict(set2) == {'o': 1.5, 'n': 3, 'g': 3.5}
    assert dict(set_) == dict(set2) == {'n': 3, 'g': 3.5}
    with Transaction(session, [keyid]):
        len(set_)
        popped = set_.pop(remove=None)
        assert popped == 'n'
        assert dict(set2) == {'n': 3, 'g': 3.5}
    assert dict(set_) == dict(set2) == {'g': 3.5}
    set_.clear()
    with Transaction(session, [keyid]):
        with raises(KeyError):
            set_.pop()


def test_pop_dict(session):
    set_ = session.set(key('test_sortedset_dict_set'),
                       {'h': 1, 'o': 1, 'n': 3, 'g': 4},
                       SortedSet)
    popped = set_.pop('o')
    assert popped == 1
    assert dict(set_) == {'h': 1, 'n': 3, 'g': 4}
    popped = set_.pop('n', score=0.5)
    assert popped == 3
    assert dict(set_) == {'h': 1, 'n': 2.5, 'g': 4}
    popped = set_.pop('n', remove=1.5)
    assert popped == 2.5
    assert dict(set_) == {'h': 1, 'g': 4}
    popped = set_.pop('g', remove=None)
    assert popped == 4
    assert dict(set_) == {'h': 1}
    popped = set_.pop('n')
    assert popped is None
    assert dict(set_) == {'h': 1}
    popped = set_.pop('n', default='default value')
    assert popped == 'default value'
    setx = session.set(key('test_sortedsetx_dict_set'),
                       {3: 1, 1: 1, 4: 3, 5: 4},
                       IntSet)
    popped = setx.pop(1)
    assert popped == 1
    assert dict(setx) == {3: 1, 4: 3, 5: 4}
    popped = setx.pop(4, score=0.5)
    assert popped == 3
    assert dict(setx) == {3: 1, 4: 2.5, 5: 4}
    popped = setx.pop(4, remove=1.5)
    assert popped == 2.5
    assert dict(setx) == {3: 1, 5: 4}
    popped = setx.pop(5, remove=None)
    assert popped == 4
    assert dict(setx) == {3: 1}
    popped = setx.pop(4)
    assert popped is None
    assert dict(setx) == {3: 1}
    popped = setx.pop(4, default='default value')
    assert popped == 'default value'


def test_pop_dict_t(session):
    session2 = get_session()
    keyid = key('test_sortedset_dict_set_t')
    set_ = session.set(keyid, {'h': 1, 'o': 1, 'n': 3, 'g': 4}, SortedSet)
    set2 = session2.get(keyid, SortedSet)
    with Transaction(session, [keyid]):
        len(set_)
        popped = set_.pop('o')
        assert popped == 1
        assert dict(set2) == {'h': 1, 'o': 1, 'n': 3, 'g': 4}
        with raises(CommitError):
            len(set_)
    assert dict(set_) == dict(set2) == {'h': 1, 'n': 3, 'g': 4}
    with Transaction(session, [keyid]):
        len(set_)
        popped = set_.pop('n', score=0.5)
        assert popped == 3
        assert dict(set2) == {'h': 1, 'n': 3, 'g': 4}
        with raises(CommitError):
            len(set_)
    assert dict(set_) == dict(set2) == {'h': 1, 'n': 2.5, 'g': 4}
    with Transaction(session, [keyid]):
        len(set_)
        popped = set_.pop('n', remove=1.5)
        assert popped == 2.5
        assert dict(set2) == {'h': 1, 'n': 2.5, 'g': 4}
        with raises(CommitError):
            len(set_)
    assert dict(set_) == dict(set2) == {'h': 1, 'g': 4}
    with Transaction(session, [keyid]):
        len(set_)
        popped = set_.pop('g', remove=None)
        assert popped == 4
        assert dict(set2) == {'h': 1, 'g': 4}
        with raises(CommitError):
            len(set_)
    assert dict(set_) == dict(set2) == {'h': 1}
    with Transaction(session, [keyid]):
        len(set_)
        popped = set_.pop('n')
        assert popped is None
        assert dict(set2) == {'h': 1}
    assert dict(set_) == dict(set2) == {'h': 1}
    with Transaction(session, [keyid]):
        len(set_)
        popped = set_.pop('n', default='default value')
        assert popped == 'default value'
        assert dict(set2) == {'h': 1}
    assert dict(set_) == dict(set2) == {'h': 1}


def test_popitem(session):
    set_ = session.set(key('test_sortedset_popitem'),
                       {'h': 1, 'o': 2, 'n': 3, 'g': 4.5},
                       SortedSet)
    popped = set_.popitem()
    assert popped == ('h', 1)
    assert dict(set_) == {'o': 2, 'n': 3, 'g': 4.5}
    popped = set_.popitem(desc=True)
    assert popped == ('g', 4.5)
    assert dict(set_) == {'o': 2, 'n': 3, 'g': 3.5}
    popped = set_.popitem(score=0.5)
    assert popped == ('o', 2)
    assert dict(set_) == {'o': 1.5, 'n': 3, 'g': 3.5}
    popped = set_.popitem(remove=0.5)
    assert popped == ('o', 1.5)
    assert dict(set_) == {'n': 3, 'g': 3.5}
    popped = set_.popitem(remove=None)
    assert popped == ('n', 3)
    assert dict(set_) == {'g': 3.5}
    set_.clear()
    with raises(KeyError):
        set_.popitem()
    setx = session.set(key('test_sortedsetx_popitem'),
                       {3: 1, 1: 2, 4: 3, 5: 4.5},
                       IntSet)
    popped = setx.popitem()
    assert popped == (3, 1)
    assert dict(setx) == {1: 2, 4: 3, 5: 4.5}
    popped = setx.popitem(desc=True)
    assert popped == (5, 4.5)
    assert dict(setx) == {1: 2, 4: 3, 5: 3.5}
    popped = setx.popitem(score=0.5)
    assert popped == (1, 2)
    assert dict(setx) == {1: 1.5, 4: 3, 5: 3.5}
    popped = setx.popitem(remove=0.5)
    assert popped == (1, 1.5)
    assert dict(setx) == {4: 3, 5: 3.5}
    popped = setx.popitem(remove=None)
    assert popped == (4, 3)
    assert dict(setx) == {5: 3.5}
    setx.clear()
    with raises(KeyError):
        setx.popitem()


def test_popitem_t(session):
    session2 = get_session()
    keyid = key('test_sortedset_popitem_t')
    set_ = session.set(keyid, {'h': 1, 'o': 2, 'n': 3, 'g': 4.5}, SortedSet)
    set2 = session2.get(keyid, SortedSet)
    with Transaction(session, [keyid]):
        len(set_)
        popped = set_.popitem()
        assert popped == ('h', 1)
        assert dict(set2) == {'h': 1, 'o': 2, 'n': 3, 'g': 4.5}
        with raises(CommitError):
            len(set_)
    assert dict(set_) == dict(set2) == {'o': 2, 'n': 3, 'g': 4.5}
    with Transaction(session, [keyid]):
        len(set_)
        popped = set_.popitem(desc=True)
        assert popped == ('g', 4.5)
        assert dict(set2) == {'o': 2, 'n': 3, 'g': 4.5}
        with raises(CommitError):
            len(set_)
    assert dict(set_) == dict(set2) == {'o': 2, 'n': 3, 'g': 3.5}
    with Transaction(session, [keyid]):
        len(set_)
        popped = set_.popitem(score=0.5)
        assert popped == ('o', 2)
        assert dict(set2) == {'o': 2, 'n': 3, 'g': 3.5}
    assert dict(set_) == dict(set2) == {'o': 1.5, 'n': 3, 'g': 3.5}
    with Transaction(session, [keyid]):
        len(set_)
        popped = set_.popitem(remove=0.5)
        assert popped == ('o', 1.5)
        assert dict(set2) == {'o': 1.5, 'n': 3, 'g': 3.5}
    assert dict(set_) == dict(set2) == {'n': 3, 'g': 3.5}
    with Transaction(session, [keyid]):
        len(set_)
        popped = set_.popitem(remove=None)
        assert popped == ('n', 3)
        assert dict(set2) == {'n': 3, 'g': 3.5}
    assert dict(set_) == dict(set2) == {'g': 3.5}
    set_.clear()
    with Transaction(session, [keyid]):
        with raises(KeyError):
            set_.popitem()


def test_clear(session):
    set_ = session.set(key('test_sortedset_clear'), S('abc'), SortedSet)
    set_.clear()
    assert len(set_) == 0
    setx = session.set(key('test_sortedsetx_clear'), S([1, 2, 3]), IntSet)
    setx.clear()
    assert len(setx) == 0


def test_update(session):
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


def test_massive_update(session):
    huge_data = dict((chr(a) * i, (a - ord('a') + 1) * i)
                     for a in range(ord('a'), ord('z') + 1)
                     for i in range(1, 101))
    set_ = session.get(key('test_sortedset_massive_update'), SortedSet)
    set_.update(huge_data)
    assert dict(set_) == huge_data
    a_to_z = set('abcdefghijklmnopqrstuvwxyz')
    set_.update(a_to_z)
    for i in a_to_z:
        huge_data[i] += 1
    assert dict(set_) == huge_data
    data = dict((chr(a), a) for a in range(ord('a'), ord('z') + 1))
    setx = session.set(key('test_sortedsetx_massive_update'), data, SortedSet)
    set_.update(setx)
    for e, score in setx.items():
        huge_data[e] += score
    assert dict(set_) == huge_data


def test_repr(session):
    keyid = key('test_sortedset_repr')
    set_ = session.set(keyid, set([1, 2, 3]), IntSet)
    expected = '<sider.sortedset.SortedSet (' + repr(keyid) + ') {1, 2, 3}>'
    assert expected == repr(set_)
    set_.update({1: 1})
    expected = '<sider.sortedset.SortedSet (' + repr(keyid) + \
               ') {2, 3, 1: 2.0}>'
    assert expected == repr(set_)
