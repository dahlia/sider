import datetime
from attest import Tests, assert_hook, raises
from sider.entity.map import Map
from sider.types import Value
from sider.datetime import utcnow
from ..env import get_session, key
from .schema import make_schema


tests = Tests()


class User(object):
    """A plain class for test."""

    def __init__(self, login, name, url=None, dob=None, created_at=None):
        self.login = login
        self.name = name
        self.url = url
        self.dob = dob
        self.created_at = created_at


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
    user = User(u'dahlia', u'Hong Minhee', url=u'http://dahlia.kr/',
                dob=datetime.date(1988, 8, 4))
    session = get_session()
    session.set(key('test_entity_map_object'), user, mapper)
    loaded = session.get(key('test_entity_map_object'), mapper)
    assert isinstance(loaded, User)
    assert loaded.login == u'dahlia'
    assert loaded.name == u'Hong Minhee'
    assert loaded.url == u'http://dahlia.kr/'
    assert loaded.dob == datetime.date(1988, 8, 4)
    assert utcnow() - loaded.created_at < datetime.timedelta(minutes=1)

