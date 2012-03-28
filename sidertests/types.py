import datetime
from attest import Tests, assert_hook, raises
from .env import get_session, key
from sider.types import ByteString, Date


tests = Tests()


@tests.test
def date():
    session = get_session()
    date = session.set(key('test_types_date'), datetime.date(1988, 8, 4), Date)
    assert date == datetime.date(1988, 8, 4)
    with raises(TypeError):
        session.set(key('test_types_date'), 1234, Date)
    session.set(key('test_types_date'), '19880804', ByteString)
    with raises(ValueError):
        session.get(key('test_types_date'), Date)

