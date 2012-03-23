try:
    from collections import Counter
except ImportError:
    from .counter_recipe import Counter
from attest import Tests, assert_hook, raises
from .env import NInt, get_session, key
from sider.types import Hash


tests = Tests()
fixture_a = {'a': 'b', 'c': 'd'}
fixture_b = {1: 'a', 2: 'b'}


@tests.test
def iterate():
    session = get_session()
    hash_ = session.set(key('test_hash_iterate'), fixture_a, Hash)
    assert set(hash_) == set('ac')
    hashx = session.set(key('test_hashx_iterate'), fixture_b, Hash(NInt))
    assert set(hashx) == set([1, 2])


@tests.test
def length():
    session = get_session()
    hash_ = session.set(key('test_hash_length'), fixture_a, Hash)
    assert len(hash_) == 2
    hashx = session.set(key('test_hashx_length'), fixture_b, Hash(NInt))
    assert len(hashx) == 2


@tests.test
def contains():
    session = get_session()
    hash_ = session.set(key('test_hash_contains'), fixture_a, Hash)
    assert 'a' in hash_
    assert 'b' not in hash_ 
    assert 'c' in hash_
    assert 1 not in hash_ 
    hashx = session.set(key('test_hashx_contains'), fixture_b, Hash(NInt))
    assert 1 in hashx
    assert 2 in hashx
    assert 4 not in hashx
    assert '1' not in hashx
    assert '4' not in hashx


@tests.test
def getitem():
    session = get_session()
    hash_ = session.set(key('test_hash_getitem'), fixture_a, Hash)
    assert hash_['a'] == 'b'
    with raises(KeyError):
        hash_['b']
    assert hash_['c'] == 'd'
    with raises(TypeError):
        hash_[object()]
    with raises(TypeError):
        hash_[1]
    hashx = session.set(key('test_hashx_getitem'), fixture_b, Hash(NInt))
    assert hashx[1] == 'a'
    assert hashx[2] == 'b'
    with raises(KeyError):
        hashx[3]
    with raises(TypeError):
        hashx[object()]
    with raises(TypeError):
        hashx['a']


@tests.test
def equals():
    session = get_session()
    hash_ = session.set(key('test_hash_equals'), fixture_a, Hash)
    hash2 = session.set(key('test_hash_equals2'), fixture_a, Hash)
    fixture_c = dict(fixture_a)
    fixture_c['e'] = 'f'
    hash3 = session.set(key('test_hash_equals3'), fixture_c, Hash)
    hash4 = session.set(key('test_hash_equals4'), fixture_b, Hash(NInt))
    emptyhash = session.set(key('test_hash_equals5'), {}, Hash)
    emptyhash2 = session.set(key('test_hash_equals5'), {}, Hash(NInt))
    assert hash_ == fixture_a
    assert hash_ != fixture_b
    assert hash_ != fixture_c
    assert hash_ == hash2 and hash2 == hash_
    assert hash_ != hash3 and hash3 != hash_
    assert hash_ != hash4 and hash4 != hash_
    assert emptyhash == emptyhash2 and emptyhash2 == emptyhash


@tests.test
def keys():
    session = get_session()
    hash_ = session.set(key('test_hash_keys'), fixture_a, Hash)
    assert set(hash_.keys()) == set('ac')
    assert len(hash_.keys()) == 2
    assert 'a' in hash_.keys()
    assert 'b' not in hash_.keys()
    assert 'c' in hash_.keys()
    hashx = session.set(key('test_hashx_keys'), fixture_b, Hash(NInt))
    assert set(hashx.keys()) == set([1, 2])
    assert len(hashx.keys()) == 2
    assert 1 in hashx.keys()
    assert 2 in hashx.keys()
    assert 3 not in hashx.keys()


@tests.test
def values():
    session = get_session()
    hash_ = session.set(key('test_hash_values'), fixture_a, Hash)
    assert Counter(hash_.values()) == Counter('bd')
    assert len(hash_.values()) == 2
    assert 'a' not in hash_.values()
    assert 'b' in hash_.values()
    assert 'd' in hash_.values()
    hashx = session.set(key('test_hashx_values'), {1: 2, 3: 4, 5: 2},
                        Hash(NInt, NInt))
    assert Counter(hashx.values()) == Counter({2: 2, 4: 1})
    assert len(hashx.values()) == 3
    assert 2 in hashx.values()
    assert 3 not in hashx.values()
    assert 4 in hashx.values()


@tests.test
def items():
    session = get_session()
    hash_ = session.set(key('test_hash_items'), fixture_a, Hash)
    assert set(hash_.items()) == set([('a', 'b'), ('c', 'd')])
    assert len(hash_.items()) == 2
    assert ('a', 'b') in hash_.items()
    assert ('b', 'b') not in hash_.items()
    assert ('c', 'c') not in hash_.items()
    assert ('c', 'd') in hash_.items()
    hashx = session.set(key('test_hashx_items'), fixture_b, Hash(NInt))
    assert set(hashx.items()) == set([(1, 'a'), (2, 'b')])
    assert len(hashx.items()) == 2
    assert (1, 'a') in hashx.items()
    assert (1, 'b') not in hashx.items()
    assert (2, 'a') not in hashx.items()
    assert (2, 'b') in hashx.items()


@tests.test
def clear():
    session = get_session()
    hash_ = session.set(key('test_hash_clear'), fixture_a, Hash)
    hash_.clear()
    assert len(hash_) == 0
    assert not list(hash_)
    hashx = session.set(key('test_hashx_clear'), fixture_b, Hash(NInt))
    hashx.clear()
    assert len(hashx) == 0
    assert not list(hashx)


@tests.test
def delitem():
    session = get_session()
    hash_ = session.set(key('test_hash_delitem'), fixture_a, Hash)
    del hash_['a']
    assert len(hash_) == 1
    assert 'a' not in hash_.keys()
    with raises(KeyError):
        del hash_['a']
    with raises(TypeError):
        del hash_[1]
    hashx = session.set(key('test_hashx_delitem'), fixture_b, Hash(NInt))
    del hashx[1]
    assert len(hashx) == 1
    assert 1 not in hashx.keys()
    with raises(KeyError):
        del hashx[1]
    with raises(TypeError):
        del hashx['a']

