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
def issubset():
    session = get_session()
    test_sets = {Set(): 'abcdefg', Set(Integer): range(1, 8)}
    fixtures = {}
    for value_type, members in test_sets.iteritems():
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
    assert not fixtures[Set()][0].issubset(fixtures[Set(Integer)][0])
    assert not fixtures[Set()][0].issubset(fixtures[Set(Integer)][1])
    assert not fixtures[Set()][0].issubset(fixtures[Set(Integer)][2])


@tests.test
def issuperset():
    session = get_session()
    test_sets = {Set(): 'abcdefg', Set(Integer): range(1, 8)}
    fixtures = {}
    for value_type, members in test_sets.iteritems():
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
    assert not fixtures[Set()][0].issuperset(fixtures[Set(Integer)][0])
    assert not fixtures[Set()][0].issuperset(fixtures[Set(Integer)][1])
    assert not fixtures[Set()][0].issuperset(fixtures[Set(Integer)][2])


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
    assert S('bdef') - set_ == S('ef')
    with raises(TypeError):
        set_ - 'bdef'
    setx = session.set(key('test_setx_difference'), S([1, 2, 3, 4]), IntSet)
    sety = session.set(key('test_setx_difference2'), S([2, 4, 5, 6]), IntSet)
    assert setx.difference(sety) == S([1, 3])
    assert setx.difference([2, 4, 5, 6]) == S([1, 3])
    assert setx.difference(S([2, 4, 5, 6])) == S([1, 3])
    assert setx - sety == S([1, 3])
    assert setx - S([2, 4, 5, 6]) == S([1, 3])
    assert S([2, 4, 5, 6]) -setx == S([5, 6])
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


@tests.test
def intersection():
    session = get_session()
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

