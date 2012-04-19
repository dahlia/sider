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


@tests.test
def length(session):
    set_ = session.set(key('test_sortedset_length'), S('abc'), SortedSet)
    assert len(set_) == 3
    setx = session.set(key('test_sortedsetx_length'), S([1, 2, 3]), IntSet)
    assert len(setx) == 3


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

