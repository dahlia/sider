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

