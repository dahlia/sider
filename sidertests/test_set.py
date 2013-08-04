from pytest import raises
from .env import NInt, get_session, key
from .env import session
from sider.types import Set
from sider.transaction import Transaction
from sider.exceptions import CommitError


S = frozenset
IntSet = Set(NInt)


def test_iterate(session):
    set_ = session.set(key('test_set_iterate'), S('abc'), Set)
    assert S(['a', 'b', 'c']) == S(set_)
    setx = session.set(key('test_setx_iterate'), S([1, 2, 3]), IntSet)
    assert S([1, 2, 3]) == S(setx)


def test_length(session):
    set_ = session.set(key('test_set_length'), S('abc'), Set)
    assert len(set_) == 3
    setx = session.set(key('test_setx_length'), S([1, 2, 3]), IntSet)
    assert len(setx) == 3


def test_contains(session):
    set_ = session.set(key('test_set_contains'), S('abc'), Set)
    assert 'a' in set_
    assert 'd' not in set_
    setx = session.set(key('test_setx_contains'), S([1, 2, 3]), IntSet)
    assert 1 in setx
    assert 4 not in setx
    assert '1' not in setx
    assert '4' not in setx


def test_equals(session):
    set_ = session.set(key('test_set_equals'), S('abc'), Set)
    set2 = session.set(key('test_set_equals2'), S('abc'), Set)
    set3 = session.set(key('test_set_equals3'), S('abcd'), Set)
    set4 = session.set(key('test_set_equals4'), S([1, 2, 3]), IntSet)
    emptyset = session.set(key('test_set_equals5'), S(), Set)
    emptyset2 = session.set(key('test_set_equals5'), S(), IntSet)
    assert set_ == set('abc')
    assert set_ != set('abcd')
    assert set_ == S('abc')
    assert set_ != S('abcd')
    assert set_ == set2 and set2 == set_
    assert set_ != set3 and set3 != set_
    assert set_ != set4 and set4 != set_
    assert emptyset == emptyset2 and emptyset2 == emptyset


def test_isdisjoint(session):
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
    # mismatched value_type NInt vs. Bulk:
    assert setd.isdisjoint(setx)
    assert setx.isdisjoint(setd)
    assert setd.isdisjoint(setxj)
    assert setd.isdisjoint(setxd)
    assert setxj.isdisjoint(setd)
    assert setxd.isdisjoint(setd)


def test_issubset(session):
    test_sets = {Set(): 'abcdefg', Set(NInt): range(1, 8)}
    fixtures = {}
    for value_type, members in test_sets.items():
        typeid = str(hash(value_type))
        d = list(members)
        e = d[1:-1]
        f = e[1:-1]
        g = S(d)
        h = S(e)
        i = S(f)
        a = session.set(key('test_set_issubset_a' + typeid), g, value_type)
        b = session.set(key('test_set_issubset_b' + typeid), h, value_type)
        c = session.set(key('test_set_issubset_c' + typeid), i, value_type)
        fixtures[value_type] = a, b, c
        assert c.issubset(a) and c <= a and c < a
        assert c.issubset(b) and c <= b and c < b
        assert c.issubset(c) and c <= c and not (c < c)
        assert c.issubset(d)
        assert c.issubset(e)
        assert c.issubset(f)
        assert c.issubset(g) and c <= g and c < g
        assert c.issubset(h) and c <= h and c < h
        assert c.issubset(i) and c <= i and not (c < i)
        assert b.issubset(a) and b <= a and b < a
        assert b.issubset(b) and b <= b and not (b < b)
        assert not b.issubset(c) and not (a <= c) and not (a < c)
        assert b.issubset(d)
        assert b.issubset(e)
        assert not b.issubset(f)
        assert b.issubset(g) and b <= g and b < g
        assert b.issubset(h) and b <= h and not (b < h)
        assert not b.issubset(i) and not (b <= i) and not (b < i)
        assert a.issubset(a) and a <= a and not (a < a)
        assert not a.issubset(b) and not (a <= b) and not (a < b)
        assert not a.issubset(c) and not (a <= c) and not (a < c)
        assert a.issubset(d)
        assert not a.issubset(e)
        assert not a.issubset(f)
        assert a.issubset(g) and a <= g and not (a < g)
        assert not a.issubset(h) and not (a <= h) and not (a < h)
        assert not a.issubset(i) and not (a <= i) and not (a < i)
        with raises(TypeError):
            a <= d
        with raises(TypeError):
            a <= e
        with raises(TypeError):
            a <= f
        with raises(TypeError):
            a < d
        with raises(TypeError):
            a < e
        with raises(TypeError):
            a < f
    assert not fixtures[Set()][0].issubset(fixtures[Set(NInt)][0])
    assert not fixtures[Set()][0].issubset(fixtures[Set(NInt)][1])
    assert not fixtures[Set()][0].issubset(fixtures[Set(NInt)][2])


def test_issuperset(session):
    test_sets = {Set(): 'abcdefg', Set(NInt): range(1, 8)}
    fixtures = {}
    for value_type, members in test_sets.items():
        typeid = str(hash(value_type))
        f = list(members)
        e = f[1:-1]
        d = e[1:-1]
        g = S(d)
        h = S(e)
        i = S(f)
        a = session.set(key('test_set_issuperset_a' + typeid), g, value_type)
        b = session.set(key('test_set_issuperset_b' + typeid), h, value_type)
        c = session.set(key('test_set_issuperset_c' + typeid), i, value_type)
        fixtures[value_type] = a, b, c
        assert c.issuperset(a) and c >= a and c > a
        assert c.issuperset(b) and c >= b and c > b
        assert c.issuperset(c) and c >= c and not (c > c)
        assert c.issuperset(d)
        assert c.issuperset(e)
        assert c.issuperset(f)
        assert c.issuperset(g) and c >= g and c > g
        assert c.issuperset(h) and c >= h and c > h
        assert c.issuperset(i) and c >= i and not (c > i)
        assert b.issuperset(a) and b >= a and b > a
        assert b.issuperset(b) and b >= b and not (b > b)
        assert not b.issuperset(c) and not (a >= c) and not (a > c)
        assert b.issuperset(d)
        assert b.issuperset(e)
        assert not b.issuperset(f)
        assert b.issuperset(g) and b >= g and b > g
        assert b.issuperset(h) and b >= h and not (b > h)
        assert not b.issuperset(i) and not (b >= i) and not (b > i)
        assert a.issuperset(a) and a >= a and not (a > a)
        assert not a.issuperset(b) and not (a >= b) and not (a > b)
        assert not a.issuperset(c) and not (a >= c) and not (a > c)
        assert a.issuperset(d)
        assert not a.issuperset(e)
        assert not a.issuperset(f)
        assert a.issuperset(g) and a >= g and not (a > g)
        assert not a.issuperset(h) and not (a >= h) and not (a > h)
        assert not a.issuperset(i) and not (a >= i) and not (a > i)
        with raises(TypeError):
            a >= d
        with raises(TypeError):
            a >= e
        with raises(TypeError):
            a >= f
        with raises(TypeError):
            a > d
        with raises(TypeError):
            a > e
        with raises(TypeError):
            a > f
    assert not fixtures[Set()][0].issuperset(fixtures[Set(NInt)][0])
    assert not fixtures[Set()][0].issuperset(fixtures[Set(NInt)][1])
    assert not fixtures[Set()][0].issuperset(fixtures[Set(NInt)][2])


def test_difference(session):
    set_ = session.set(key('test_set_difference'), S('abcd'), Set)
    set2 = session.set(key('test_set_difference2'), S('bde1'), Set)
    set3 = session.set(key('test_set_difference3'), S('az'), Set)
    assert set_.difference() == S('abcd')
    assert set_.difference(set2) == S('ac')
    assert set_.difference(set2, set3) == S('c')
    assert set_.difference(set2, 'az') == S('c')
    assert set_.difference(set2, S('az')) == S('c')
    assert set_.difference('bdef') == S('ac')
    assert set_.difference('bdef', set3) == S('c')
    assert set_.difference('bdef', 'az') == S('c')
    assert set_.difference('bdef', S('az')) == S('c')
    assert set_.difference(S('bdef')) == S('ac')
    assert set_.difference(S('bdef'), set3) == S('c')
    assert set_.difference(S('bdef'), 'az') == S('c')
    assert set_.difference(S('bdef'), S('az')) == S('c')
    assert set_ - set2 == S('ac')
    assert set_ - S('bdef') == S('ac')
    assert S('bdef') - set_ == S('ef')
    with raises(TypeError):
        set_ - 'bdef'
    setx = session.set(key('test_setx_difference'), S([1, 2, 3, 4]), IntSet)
    sety = session.set(key('test_setx_difference2'), S([2, 4, 5, 6]), IntSet)
    setz = session.set(key('test_setx_difference3'), S([1, 7]), IntSet)
    assert setx.difference() == S([1, 2, 3, 4])
    assert setx.difference(sety) == S([1, 3])
    assert setx.difference(sety, setz) == S([3])
    assert setx.difference(sety, [1, 7]) == S([3])
    assert setx.difference(sety, S([1, 7])) == S([3])
    assert setx.difference([2, 4, 5, 6]) == S([1, 3])
    assert setx.difference([2, 4, 5, 6], setz) == S([3])
    assert setx.difference([2, 4, 5, 6], [1, 7]) == S([3])
    assert setx.difference([2, 4, 5, 6], S([1, 7])) == S([3])
    assert setx.difference(S([2, 4, 5, 6])) == S([1, 3])
    assert setx.difference(S([2, 4, 5, 6]), [1, 7]) == S([3])
    assert setx.difference(S([2, 4, 5, 6]), S([1, 7])) == S([3])
    assert setx - sety == S([1, 3])
    assert setx - S([2, 4, 5, 6]) == S([1, 3])
    assert S([2, 4, 5, 6]) - setx == S([5, 6])
    with raises(TypeError):
        setx - [2, 4, 5, 6]
    # mismatched value_type NInt vs. Bulk:
    assert set2 == set2.difference(setx)
    assert set2 == set2.difference(setx, setz)
    assert setx == setx.difference(set2)
    assert setx == setx.difference(set2, set3)


def test_symmetric_difference(session):
    set_ = session.set(key('test_set_symmdiff'), S('abcd'), Set)
    set2 = session.set(key('test_set_symmdiff2'), S('bde1'), Set)
    assert set_.symmetric_difference(set2) == S('ace1')
    assert set_.symmetric_difference('bdef') == S('acef')
    assert set_.symmetric_difference(S('bdef')) == S('acef')
    assert set_ ^ set2 == S('ace1')
    assert set_ ^ S('bdef') == S('acef')
    assert S('bdef') ^ set_ == S('acef')
    with raises(TypeError):
        set_ ^ 'bdef'
    setx = session.set(key('test_setx_symmdiff'), S([1, 2, 3, 4]), IntSet)
    sety = session.set(key('test_setx_symmdiff2'), S([2, 4, 5, 6]), IntSet)
    assert setx.symmetric_difference(sety) == S([1, 3, 5, 6])
    assert setx.symmetric_difference([2, 4, 5, 6]) == S([1, 3, 5, 6])
    assert setx.symmetric_difference(S([2, 4, 5, 6])) == S([1, 3, 5, 6])
    assert setx ^ sety == S([1, 3, 5, 6])
    assert setx ^ S([2, 4, 5, 6]) == S([1, 3, 5, 6])
    assert S([2, 4, 5, 6]) ^ setx == S([1, 3, 5, 6])
    with raises(TypeError):
        setx ^ [2, 4, 5, 6]
    # mismatched value_type NInt vs. Bulk:
    assert setx.union(set2) == setx.symmetric_difference(set2)
    assert set2.union(setx) == set2.symmetric_difference(setx)


def test_union(session):
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
    assert S('cde') | set_ == S('abcde')
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
    assert S([3, 4, 5]) | setx == S([1, 2, 3, 4, 5])
    with raises(TypeError):
        setx | [3, 4, 5]
    assert set_.union(setx) == S(['a', 'b', 'c', 1, 2, 3])
    assert set_.union(setx, sety) == S(['a', 'b', 'c', 1, 2, 3, 4, 5])
    assert (set_.union(set2, setx, sety)
            == S(['a', 'b', 'c', 'd', 'e', 1, 2, 3, 4, 5]))
    assert set_ | setx == S(['a', 'b', 'c', 1, 2, 3])


def test_intersection(session):
    set_ = session.set(key('test_set_intersection'), S('abc'), Set)
    set2 = session.set(key('test_set_intersection2'), S('bcd'), Set)
    set3 = session.set(key('test_set_intersection3'), S('bef'), Set)
    assert set_.intersection('bcde') == S('bc')
    assert set_.intersection('bcde', 'cdef') == S('c')
    assert set_.intersection(S('bcde')) == S('bc')
    assert set_.intersection(S('bcde'), 'cdef') == S('c')
    assert set_.intersection(S('bcde'), S('cdef')) == S('c')
    assert set_.intersection(set2) == S('bc')
    assert set_.intersection(set2, set3) == S('b')
    assert set_.intersection(set2, set3, 'bcfg') == S('b')
    assert set_.intersection(set2, set3, 'acfg') == S()
    assert set_ & S('bcd') == S('bc')
    assert set_ & set2 == S('bc')
    assert S('bcd') & set_ == S('bc')
    with raises(TypeError):
        set_ & 'cde'
    setx = session.set(key('test_setx_intersection'), S([1, 2, 3]), IntSet)
    sety = session.set(key('test_setx_intersection2'), S([2, 3, 4]), IntSet)
    setz = session.set(key('test_setx_intersection3'), S([1, 2, 5]), IntSet)
    assert setx.intersection([2, 3, 4]) == S([2, 3])
    assert setx.intersection([2, 3, 4], [1, 2, 5]) == S([2])
    assert setx.intersection(S([2, 3, 4])) == S([2, 3])
    assert setx.intersection(S([2, 3, 4]), [1, 2, 5]) == S([2])
    assert setx.intersection(S([2, 3, 4]), S([1, 2, 5])) == S([2])
    assert setx.intersection(sety) == S([2, 3])
    assert setx.intersection(sety, setz) == S([2])
    assert setx.intersection(sety, setz, [1, 2, 5]) == S([2])
    assert setx & S([2, 3, 4]) == S([2, 3])
    assert setx & sety == S([2, 3])
    assert S([2, 3, 4]) & setx == S([2, 3])
    with raises(TypeError):
        setx & [3, 4, 5]
    assert set_.intersection(setx) == S([])
    assert set_.intersection(setx, sety) == S([])
    assert set_.intersection(set2, setx, sety) == S([])
    assert set_ & setx == S([])


def test_add(session):
    set_ = session.set(key('test_set_add'), S('abc'), Set)
    set_.add('d')
    assert set_ == S('abcd')
    set_.add('d')
    assert set_ == S('abcd')
    with raises(TypeError):
        set_.add(1)
    setx = session.set(key('test_setx_add'), S([1, 2, 3]), IntSet)
    setx.add(4)
    assert setx == S([1, 2, 3, 4])
    setx.add(4)
    assert setx == S([1, 2, 3, 4])
    with raises(TypeError):
        setx.add('a')


def test_discard(session):
    set_ = session.set(key('test_set_discard'), S('abc'), Set)
    set_.discard('a')
    assert set_ == S('bc')
    set_.discard('a')
    assert set_ == S('bc')
    set_.discard(1)
    assert set_ == S('bc')
    setx = session.set(key('test_setx_discard'), S([1, 2, 3]), IntSet)
    setx.discard(1)
    assert setx == S([2, 3])
    setx.discard(1)
    assert setx == S([2, 3])
    setx.discard('a')
    assert setx == S([2, 3])


def test_pop(session):
    expected = set('abc')
    set_ = session.set(key('test_set_pop'), expected, Set)
    popped = set_.pop()
    assert popped in expected
    expected.remove(popped)
    assert set_ == expected
    popped = set_.pop()
    assert popped in expected
    expected.remove(popped)
    assert set_ == expected
    popped = set_.pop()
    assert popped in expected
    assert len(set_) == 0
    expected.remove(popped)
    assert len(expected) == 0
    with raises(KeyError):
        set_.pop()


def test_pop_t(session):
    session2 = get_session()
    expected = set('abc')
    keyid = key('test_set_pop_t')
    set_ = session.set(keyid, expected, Set)
    setx = session2.get(keyid, Set)
    with Transaction(session, [keyid]):
        card = len(set_)
        assert card == 3
        popped = set_.pop()
        assert setx == expected
    assert popped in expected
    expected.remove(popped)
    assert set_ == set(setx) == expected
    with Transaction(session, [keyid]):
        card = len(set_)
        assert card == 2
        popped = set_.pop()
        assert setx == expected
    assert popped in expected
    expected.remove(popped)
    assert set_ == set(setx) == expected
    with Transaction(session, [keyid]):
        card = len(set_)
        assert card == 1
        popped = set_.pop()
        assert setx == expected
    assert popped in expected
    assert len(set_) == len(setx) == 0
    expected.remove(popped)
    assert len(expected) == 0
    with Transaction(session, [keyid]):
        with raises(KeyError):
            set_.pop()


def test_clear(session):
    set_ = session.set(key('test_set_clear'), S('abc'), Set)
    set_.clear()
    assert len(set_) == 0


def test_update(session):
    def reset():
        return session.set(key('test_set_update'), S('abc'), Set)
    set_ = reset()
    set2 = session.set(key('test_set_update2'), S('cde'), Set)
    set3 = session.set(key('test_set_update3'), S('def'), Set)
    set_.update('cde')
    assert set_ == S('abcde')
    reset()
    set_.update('cde', 'def')
    assert set_ == S('abcdef')
    reset()
    set_.update(S('cde'))
    assert set_ == S('abcde')
    reset()
    set_.update(S('cde'), 'def')
    assert set_ == S('abcdef')
    reset()
    set_.update(S('cde'), S('def'))
    assert set_ == S('abcdef')
    reset()
    set_.update(set2)
    assert set_ == S('abcde')
    reset()
    set_.update(set2, set3)
    assert set_ == S('abcdef')
    reset()
    set_.update(set2, set3, 'adfg')
    assert set_ == S('abcdefg')
    reset()
    set_ |= S('cde')
    assert set_ == S('abcde')
    reset()
    set_ |= set2
    assert set_ == S('abcde')
    with raises(TypeError):
        set_ |= 'cde'
    def resetx():
        return session.set(key('test_setx_union'), S([1, 2, 3]), IntSet)
    setx = resetx()
    sety = session.set(key('test_setx_union2'), S([3, 4, 5]), IntSet)
    setz = session.set(key('test_setx_union3'), S([4, 5, 6]), IntSet)
    setx.update([3, 4, 5])
    assert setx == S([1, 2, 3, 4, 5])
    resetx()
    setx.update([3, 4, 5], [4, 5, 6])
    assert setx == S([1, 2, 3, 4, 5, 6])
    resetx()
    setx.update(S([3, 4, 5]))
    assert setx == S([1, 2, 3, 4, 5])
    resetx()
    setx.update(S([3, 4, 5]), [4, 5, 6])
    assert setx == S([1, 2, 3, 4, 5, 6])
    resetx()
    setx.update(S([3, 4, 5]), S([4, 5, 6]))
    assert setx == S([1, 2, 3, 4, 5, 6])
    resetx()
    setx.update(sety)
    assert setx == S([1, 2, 3, 4, 5])
    resetx()
    setx.update(sety, setz)
    assert setx == S([1, 2, 3, 4, 5, 6])
    resetx()
    setx.update(sety, setz, [1, 4, 6, 7])
    assert setx == S([1, 2, 3, 4, 5, 6, 7])
    resetx()
    setx |= S([3, 4, 5])
    assert setx == S([1, 2, 3, 4, 5])
    resetx()
    setx |= sety
    assert setx == S([1, 2, 3, 4, 5])
    with raises(TypeError):
        setx |= [3, 4, 5]
    with raises(TypeError):
        set_.update(setx)
    with raises(TypeError):
        set_ |= setx == S(['a', 'b', 'c', 1, 2, 3])


def test_massive_update(session):
    huge_data = set('{0}'.format(i) for i in range(1010))
    set_ = session.get(key('test_set_massive_update'), Set)
    set_.update(huge_data)
    assert set(set_) == huge_data


def test_update_t(session):
    session2 = get_session()
    keyid = key('test_set_update_t')
    keyid2 = key('test_set_update_t2')
    def reset():
        return session.set(keyid, S('abc'), Set)
    set_ = reset()
    set2 = session.set(keyid2, S('cde'), Set)
    setx = session2.get(keyid, Set)
    with Transaction(session, [keyid]):
        card = len(set_)
        assert card == 3
        set_.update('cde')
        assert setx == S('abc')
        with raises(CommitError):
            len(set_)
    assert set_ == S(setx) == S('abcde')
    set_ = reset()
    with Transaction(session, [keyid]):
        card = len(set_)
        assert card == 3
        set_.update(set2)
        assert setx == S('abc')
        with raises(CommitError):
            len(set_)
    assert set_ == S(setx) == S('abcde')
    set_ = reset()
    with Transaction(session, [keyid]):
        card = len(set_)
        assert card == 3
        set_.update(set2, 'adfg')
        assert setx == S('abc')
        with raises(CommitError):
            len(set_)
    assert set_ == S(setx) == S('abcdefg')


def test_intersection_update(session):
    def reset():
        return session.set(key('test_set_intersection_update'), S('abc'), Set)
    set_ = reset()
    set2 = session.set(key('test_set_intersection_update2'), S('bcd'), Set)
    set3 = session.set(key('test_set_intersection_update3'), S('bef'), Set)
    set_.intersection_update('bcde')
    assert set_ == S('bc')
    reset()
    set_.intersection_update('bcde', 'cdef')
    assert set_ == S('c')
    reset()
    set_.intersection_update(S('bcde'))
    assert set_ == S('bc')
    reset()
    set_.intersection_update(S('bcde'), 'cdef')
    assert set_ == S('c')
    reset()
    set_.intersection_update(S('bcde'), S('cdef'))
    assert set_ == S('c')
    reset()
    set_.intersection_update(set2)
    assert set_ == S('bc')
    reset()
    set_.intersection_update(set2, set3)
    assert set_ == S('b')
    reset()
    set_.intersection_update(set2, set3, 'bcfg')
    assert set_ == S('b')
    reset()
    set_.intersection_update(set2, set3, 'acfg')
    assert set_ == S()
    reset()
    set_ &= S('bcd')
    assert set_ == S('bc')
    reset()
    set_ &= set2
    assert set_ == S('bc')
    reset()
    with raises(TypeError):
        set_ &= 'cde'
    def resetx():
        return session.set(key('test_setx_intersection_update'),
                           S([1, 2, 3]), IntSet)
    setx = resetx()
    sety = session.set(key('test_setx_intersection_update2'),
                       S([2, 3, 4]), IntSet)
    setz = session.set(key('test_setx_intersection_update3'),
                       S([1, 2, 5]), IntSet)
    setx.intersection_update([2, 3, 4])
    assert setx == S([2, 3])
    resetx()
    setx.intersection_update([2, 3, 4], [1, 2, 5])
    assert setx == S([2])
    resetx()
    setx.intersection_update(S([2, 3, 4]))
    assert setx == S([2, 3])
    resetx()
    setx.intersection_update(S([2, 3, 4]), [1, 2, 5])
    assert setx == S([2])
    resetx()
    setx.intersection_update(S([2, 3, 4]), S([1, 2, 5]))
    assert setx == S([2])
    resetx()
    setx.intersection_update(sety)
    assert setx == S([2, 3])
    resetx()
    setx.intersection_update(sety, setz)
    assert setx == S([2])
    resetx()
    setx.intersection_update(sety, setz, [1, 2, 5])
    assert setx == S([2])
    resetx()
    setx &= S([2, 3, 4])
    assert setx == S([2, 3])
    resetx()
    setx &= sety
    assert setx == S([2, 3])
    resetx()
    with raises(TypeError):
        setx &= [3, 4, 5]
    resetx()
    set_.intersection_update(setx)
    assert set_ == S([])
    resetx()
    set_.intersection_update(setx, sety)
    assert set_ == S([])
    resetx()
    set_.intersection_update(set2, setx, sety)
    assert set_ == S([])


def test_intersection_update_t(session):
    session2 = get_session()
    keyid = key('test_set_intersection_update_t')
    keyid2 = key('test_set_intersection_update_t2')
    set_ = session.set(keyid, S('abc'), Set)
    set2 = session.set(keyid2, S('bcd'), Set)
    setx = session2.get(keyid, Set)
    with Transaction(session, [keyid, keyid2]):
        card = len(set_)
        assert card == 3
        set_.intersection_update(set2)
        assert setx == S('abc')
    assert set_ == S(setx) == S('bc')
    with Transaction(session, [keyid, keyid2]):
        set_.intersection_update(set2)
        with raises(CommitError):
            len(set_)


def test_difference_update(session):
    def reset():
        return session.set(key('test_set_difference_update'), S('abcd'), Set)
    set_ = reset()
    set2 = session.set(key('test_set_difference_update2'), S('bde1'), Set)
    set3 = session.set(key('test_set_difference_update3'), S('az'), Set)
    set_.difference_update()
    assert set_ == S('abcd')
    reset()
    set_.difference_update(set2)
    assert set_ == S('ac')
    reset()
    set_.difference_update(set2, set3)
    assert set_ == S('c')
    reset()
    set_.difference_update(set2, 'az')
    assert set_ == S('c')
    reset()
    set_.difference_update(set2, S('az'))
    assert set_ == S('c')
    reset()
    set_.difference_update('bdef')
    assert set_ == S('ac')
    reset()
    set_.difference_update('bdef', set3)
    assert set_ == S('c')
    reset()
    set_.difference_update('bdef', 'az')
    assert set_ == S('c')
    reset()
    set_.difference_update('bdef', S('az'))
    assert set_ == S('c')
    reset()
    set_.difference_update(S('bdef'))
    assert set_ == S('ac')
    reset()
    set_.difference_update(S('bdef'), set3)
    assert set_ == S('c')
    reset()
    set_.difference_update(S('bdef'), 'az')
    assert set_ == S('c')
    reset()
    set_.difference_update(S('bdef'), S('az'))
    assert set_ == S('c')
    reset()
    set_ -= set2
    assert set_ == S('ac')
    reset()
    set_ -= S('bdef')
    assert set_ == S('ac')
    reset()
    with raises(TypeError):
        set_ -= 'bdef'
    def resetx():
        return session.set(key('test_setx_difference_update'),
                           S([1, 2, 3, 4]), IntSet)
    setx = resetx()
    sety = session.set(key('test_setx_difference_update2'),
                       S([2, 4, 5, 6]), IntSet)
    setz = session.set(key('test_setx_difference_update3'),
                       S([1, 7]), IntSet)
    setx.difference_update()
    assert setx == S([1, 2, 3, 4])
    resetx()
    setx.difference_update(sety)
    assert setx == S([1, 3])
    resetx()
    setx.difference_update(sety, setz)
    assert setx == S([3])
    resetx()
    setx.difference_update(sety, [1, 7])
    assert setx == S([3])
    resetx()
    setx.difference_update(sety, S([1, 7]))
    assert setx == S([3])
    resetx()
    setx.difference_update([2, 4, 5, 6])
    assert setx == S([1, 3])
    resetx()
    setx.difference_update([2, 4, 5, 6], setz)
    assert setx == S([3])
    resetx()
    setx.difference_update([2, 4, 5, 6], [1, 7])
    assert setx == S([3])
    resetx()
    setx.difference_update([2, 4, 5, 6], S([1, 7]))
    assert setx == S([3])
    resetx()
    setx.difference_update(S([2, 4, 5, 6]))
    assert setx == S([1, 3])
    resetx()
    setx.difference_update(S([2, 4, 5, 6]), [1, 7])
    assert setx == S([3])
    resetx()
    setx.difference_update(S([2, 4, 5, 6]), S([1, 7]))
    assert setx == S([3])
    resetx()
    setx.difference_update(['1', '2', 3])
    assert setx == S([1, 2, 4])
    resetx()
    setx -= sety
    assert setx == S([1, 3])
    resetx()
    setx -= S([2, 4, 5, 6])
    assert setx == S([1, 3])
    resetx()
    with raises(TypeError):
        setx - [2, 4, 5, 6]
    # mismatched value_type NInt vs. Bulk:
    reset()
    resetx()
    set2.difference_update(setx)
    assert set2 == S('bde1')
    reset()
    set2.difference_update(setx, setz)
    assert set2 == S('bde1')
    reset()
    resetx()
    setx.difference_update(set2)
    assert setx == S([1, 2, 3, 4])
    resetx()
    setx.difference_update(set2, set3)
    assert setx == S([1, 2, 3, 4])


def test_difference_update_t(session):
    session2 = get_session()
    keyid = key('test_set_difference_update_t')
    keyid2 = key('test_set_difference_update_t2')
    set_ = session.set(keyid, S('abcd'), Set)
    set2 = session.set(keyid2, S('bde1'), Set)
    setx = session2.get(keyid, Set)
    with Transaction(session, [keyid, keyid2]):
        card = len(set_)
        assert card == 4
        set_.difference_update(set2)
        assert setx == S('abcd')
    assert set_ == S(setx) == S('ac')
    with Transaction(session, [keyid, keyid2]):
        set_.difference_update(set2)
        with raises(CommitError):
            len(set_)


def test_symmetric_difference_update(session):
    def reset():
        return session.set(key('test_set_symmdiff'), S('abcd'), Set)
    set_ = reset()
    set2 = session.set(key('test_set_symmdiff2'), S('bde1'), Set)
    set_.symmetric_difference_update(set2)
    assert set_ == S('ace1')
    reset()
    set_.symmetric_difference_update('bdef')
    assert set_ == S('acef')
    reset()
    set_.symmetric_difference_update(S('bdef'))
    assert set_ == S('acef')
    reset()
    set_ ^= set2
    assert set_ == S('ace1')
    reset()
    set_ ^= S('bdef')
    assert set_ == S('acef')
    reset()
    with raises(TypeError):
        set_ ^= 'bdef'
    def resetx():
        return session.set(key('test_setx_symmdiff'), S([1, 2, 3, 4]), IntSet)
    setx = resetx()
    sety = session.set(key('test_setx_symmdiff2'), S([2, 4, 5, 6]), IntSet)
    setx.symmetric_difference_update(sety)
    assert setx == S([1, 3, 5, 6])
    resetx()
    setx.symmetric_difference_update([2, 4, 5, 6])
    assert setx == S([1, 3, 5, 6])
    resetx()
    setx.symmetric_difference_update(S([2, 4, 5, 6]))
    assert setx == S([1, 3, 5, 6])
    resetx()
    setx ^= sety
    assert setx == S([1, 3, 5, 6])
    resetx()
    setx ^= S([2, 4, 5, 6])
    assert setx == S([1, 3, 5, 6])
    with raises(TypeError):
        setx ^= [2, 4, 5, 6]
    # mismatched value_type NInt vs. Bulk:
    resetx()
    with raises(TypeError):
        setx.symmetric_difference_update(set2)
    reset()
    with raises(TypeError):
        set2.symmetric_difference_update(setx)


def test_symmetric_difference_update_t(session):
    session2 = get_session()
    keyid = key('test_set_symmdiff_t')
    keyid2 = key('test_set_symmdiff_t2')
    set_ = session.set(keyid, S('abcd'), Set)
    set2 = session.set(keyid2, S('bde1'), Set)
    setx = session2.get(keyid, Set)
    with Transaction(session, [keyid, keyid2]):
        card = len(set_)
        assert card == 4
        set_.symmetric_difference_update(set2)
        assert setx == S('abcd')
    assert set_ == S(setx) == S('ace1')
    with Transaction(session, [keyid, keyid2]):
        set_.symmetric_difference_update(set2)
        with raises(CommitError):
            len(set_)


def test_repr(session):
    keyid = key('test_set_repr')
    set_ = session.set(keyid, set([1, 2, 3]), IntSet)
    assert '<sider.set.Set (' + repr(keyid) + ') {1, 2, 3}>' == repr(set_)
