try:
    from collections import Counter
except ImportError:
    from .counter_recipe import Counter
from pytest import raises
from .env import NInt, get_session, key
from .env import session
from sider.types import Hash
from sider.transaction import Transaction
from sider.exceptions import CommitError


fixture_a = {'a': 'b', 'c': 'd'}
fixture_b = {1: 'a', 2: 'b'}


def test_iterate(session):
    hash_ = session.set(key('test_hash_iterate'), fixture_a, Hash)
    assert set(hash_) == set('ac')
    hashx = session.set(key('test_hashx_iterate'), fixture_b, Hash(NInt))
    assert set(hashx) == set([1, 2])


def test_length(session):
    hash_ = session.set(key('test_hash_length'), fixture_a, Hash)
    assert len(hash_) == 2
    hashx = session.set(key('test_hashx_length'), fixture_b, Hash(NInt))
    assert len(hashx) == 2


def test_contains(session):
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


def test_getitem(session):
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


def test_equals(session):
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


def test_keys(session):
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


def test_values(session):
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


def test_items(session):
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


def test_clear(session):
    hash_ = session.set(key('test_hash_clear'), fixture_a, Hash)
    hash_.clear()
    assert len(hash_) == 0
    assert not list(hash_)
    hashx = session.set(key('test_hashx_clear'), fixture_b, Hash(NInt))
    hashx.clear()
    assert len(hashx) == 0
    assert not list(hashx)


def test_delitem(session):
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


def test_delitem_t(session):
    session2 = get_session()
    keyid = key('test_hash_delitem_t')
    hash_ = session.set(keyid, fixture_a, Hash)
    hashx = session2.get(keyid, Hash)
    with Transaction(session, [keyid]):
        len(hash_)
        del hash_['a']
        assert 'a' in hashx
        with raises(CommitError):
            len(hash_)
    assert len(hash_) == 1
    assert 'a' not in hash_
    assert 'a' not in hashx


def test_setitem(session):
    hash_ = session.set(key('test_hash_setitem'), fixture_a, Hash)
    hash_['a'] = 'changed'
    assert len(hash_) == 2
    assert hash_['a'] == 'changed'
    assert 'a' in hash_.keys()
    hash_['new'] = 'added'
    assert len(hash_) == 3
    assert hash_['new'] == 'added'
    assert 'new' in hash_.keys()
    with raises(TypeError):
        hash_[1] = 'a'
    with raises(TypeError):
        hash_['abc'] = 1
    hashx = session.set(key('test_hashx_setitem'), fixture_b, Hash(NInt))
    hashx[1] = 'changed'
    assert len(hashx) == 2
    assert hashx[1] == 'changed'
    assert 1 in hashx.keys()
    hashx[1234] = 'added'
    assert len(hashx) == 3
    assert hashx[1234] == 'added'
    assert 1234 in hashx.keys()
    with raises(TypeError):
        hashx[1] = 1234
    with raises(TypeError):
        hashx['invalid'] = 'val'


def test_setdefault(session):
    hash_ = session.set(key('test_hash_setdefault'), fixture_a, Hash)
    curval = hash_.setdefault('a', 'would not get changed')
    assert curval == hash_['a'] == 'b'
    assert len(hash_) == 2
    curval = hash_.setdefault('added', 'default value')
    assert len(hash_) == 3
    assert 'added' in hash_
    assert curval == hash_['added'] == 'default value'
    with raises(TypeError):
        hash_.setdefault(1, 'default')
    with raises(TypeError):
        hash_.setdefault('key', 1234)
    hashx = session.set(key('test_hashx_setdefault'), fixture_b, Hash(NInt))
    curval = hashx.setdefault(1, 'would not get changed')
    assert curval == hashx[1] == 'a'
    assert len(hashx) == 2
    curval = hashx.setdefault(1234, 'default value')
    assert len(hashx) == 3
    assert 1234 in hashx
    assert curval == hashx[1234] == 'default value'
    with raises(TypeError):
        hashx.setdefault('invalid', 'default')
    with raises(TypeError):
        hashx.setdefault('key', 1234)


def test_setdefault_t(session):
    session2 = get_session()
    keyid = key('test_hash_setdefault_t')
    hash_ = session.set(keyid, fixture_a, Hash)
    hashx = session2.get(keyid, Hash)
    with Transaction(session, [keyid]):
        curval = hash_.setdefault('a', 'would not get changed')
        assert curval == hashx['a'] == 'b'
    assert curval == hash_['a'] == hashx['a'] == 'b'
    assert len(hash_) == len(hashx) == 2
    with Transaction(session, [keyid]):
        curval = hash_.setdefault('added', 'default value')
        assert curval == 'default value'
        assert 'added' not in hashx
        with raises(CommitError):
            len(hash_)
    assert len(hash_) == len(hashx) == 3
    assert 'added' in hash_
    assert 'added' in hashx
    assert curval == hash_['added'] == hashx['added'] == 'default value'


def test_update(session):
    hash_ = session.set(key('test_hash_update'), fixture_a, Hash)
    hash_.update({'c': 'changed', 'new': 'value'})
    assert dict(hash_) == {'a': 'b', 'c': 'changed', 'new': 'value'}
    hash_.update([('new2', 'value'), ('new', 'changed')])
    assert dict(hash_) == {'a': 'b', 'c': 'changed',
                           'new': 'changed', 'new2': 'value'}
    hash_.update({'b': 'new', 'a': 'changed'}, d='new', new2='changed')
    assert dict(hash_) == {'a': 'changed', 'b': 'new', 'c': 'changed',
                           'd': 'new', 'new': 'changed', 'new2': 'changed'}
    hash_.update([('e', 'new'), ('new', 'changed2')],
                 c='changed2', f='new')
    assert dict(hash_) == {'a': 'changed', 'b': 'new', 'c': 'changed2',
                           'd': 'new', 'e': 'new', 'f': 'new',
                           'new': 'changed2', 'new2': 'changed'}
    hash_.update(b='changed', g='new')
    assert dict(hash_) == {'a': 'changed', 'b': 'changed', 'c': 'changed2',
                           'd': 'new', 'e': 'new', 'f': 'new', 'g': 'new',
                           'new': 'changed2', 'new2': 'changed'}
    with raises(TypeError):
        hash_.update({1: 'val'})
    with raises(TypeError):
        hash_.update({'key': 1234})
    with raises(TypeError):
        hash_.update([(1, 'val')])
    with raises(TypeError):
        hash_.update([('key', 1234)])
    with raises(TypeError):
        hash_.update(key=1234)
    with raises(TypeError):
        hash_.update([1, 2, 3, 4])
    with raises(ValueError):
        hash_.update([(1, 2, 3), (4, 5, 6)])
    with raises(TypeError):
        hash_.update(1234)
    hashx = session.set(key('test_hashx_update'), fixture_b, Hash(NInt))
    hashx.update({2: 'changed', 3: 'new'})
    assert dict(hashx) == {1: 'a', 2: 'changed', 3: 'new'}
    hashx.update([(3, 'changed'), (4, 'new')])
    assert dict(hashx) == {1: 'a', 2: 'changed', 3: 'changed', 4: 'new'}
    with raises(TypeError):
        hashx.update({'invalid': 'val'})
    with raises(TypeError):
        hashx.update({1234: 4567})
    with raises(TypeError):
        hashx.update([('invalid', 'val')])
    with raises(TypeError):
        hashx.update([(1234, 4567)])
    with raises(TypeError):
        hashx.update(invalid='val')
    with raises(TypeError):
        hashx.update([1, 2, 3, 4])
    with raises(ValueError):
        hashx.update([(1, 2, 3), (4, 5, 6)])
    with raises(TypeError):
        hashx.update(1234)


def test_massive_update(session):
    huge_data = dict(('{0}'.format(i), chr(ord('a') + (i % 26)) * i)
                     for i in range(1235))
    hash_ = session.get(key('test_hash_massive_update'), Hash)
    hash_.update(huge_data)
    assert dict(hash_) == huge_data


def test_repr(session):
    keyid = key('test_hash_repr')
    hash_ = session.set(keyid, {1: 2, 3: 4, 5: 6}, Hash(NInt, NInt))
    expected = '<sider.hash.Hash (' + repr(keyid) + ') {1: 2, 3: 4, 5: 6}>'
    assert expected == repr(hash_)
