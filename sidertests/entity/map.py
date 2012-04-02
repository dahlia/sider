import datetime
import hashlib
from attest import Tests, assert_hook, raises
from sider.entity.map import Map
from sider.entity.exceptions import KeyFieldError
from sider.types import Value, Hash
from sider.datetime import utcnow
from ..env import get_session, key
from .schema import make_schema


tests = Tests()


class User(object):
    """A plain class for test."""

    def __init__(self, login, password, name, url=None, dob=None,
                 created_at=None):
        self.login = login
        self.password = password
        self.name = name
        self.url = url
        self.dob = dob
        self.created_at = created_at

    @property
    def password(self):
        return Password(self._password)

    @password.setter
    def password(self, password):
        self._password = Password.hash(password)


class Password(object):
    """Mock string."""

    @staticmethod
    def hash(password):
        if isinstance(password, Password):
            return password.password_hash
        return hashlib.sha1(password).digest()

    def __init__(self, password_hash):
        self.password_hash

    def __eq__(self, other):
        if isinstance(other, Password):
            return other.password_hash == self.password_hash
        elif isinstance(other, basestring):
            return self.hash(other) == self.password_hash
        return False

    def __ne__(self, other):
        return not (self == other)


def make_mapper():
    user_schema = make_schema()
    mapper = Map(user_schema, User)
    return mapper, user_schema


@tests.test
def map_():
    mapper, schema = make_mapper()
    assert isinstance(mapper, Value)
    assert mapper.schema is schema
    assert mapper.cls is User


@tests.test
def map_arg_error():
    with raises(TypeError):
        Map((), User)
    with raises(TypeError):
        Map(make_schema(), ())


@tests.test
def map_object():
    mapper, schema = make_mapper()
    user = User(u'dahlia', 'secret', u'Hong Minhee', url=u'http://dahlia.kr/',
                dob=datetime.date(1988, 8, 4))
    session = get_session()
    session.set(key('test_entity_map_object'), user, mapper)
    loaded = session.get(key('test_entity_map_object'), mapper)
    assert isinstance(loaded, User)
    assert loaded.login == u'dahlia'
    assert loaded._password == Password.hash('secret')
    assert loaded.name == u'Hong Minhee'
    assert loaded.url == u'http://dahlia.kr/'
    assert loaded.dob == datetime.date(1988, 8, 4)
    assert utcnow() - loaded.created_at < datetime.timedelta(minutes=1)
    hash_ = session.get(key('test_entity_map_object'), Hash)
    assert hash_['password'] == Password.hash('secret')
    user2 = User(u'dahlia', 'secret', u'Doppelg\xe4nger')
    with raises(KeyFieldError):
        session.set(key('test_entity_map_object'), user2, mapper)
    with raises(TypeError):
        session.set(key('test_entity_map_object'), 1234, mapper)


@tests.test
def identity_map():
    mapper, schema = make_mapper()
    user = User(u'dahlia', 'secret', u'Hong Minhee', url=u'http://dahlia.kr/',
                dob=datetime.date(1988, 8, 4))
    session = get_session()
    stored = session.set(key('test_entity_map_identity_map'), user, mapper)
    assert stored is user
    assert session.identity_map[mapper]['dahlia'] is user
    loaded = session.get(key('test_entity_map_identity_map'), mapper)
    assert loaded is user
    loaded2 = session.get(key('test_entity_map_identity_map'), mapper)
    assert loaded2 is user

