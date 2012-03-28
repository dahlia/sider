import datetime
from attest import Tests, assert_hook, raises
from .env import get_session, key
from sider.types import ByteString, Date, DateTime
from sider.datetime import FixedOffset


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


@tests.test
def datetime_():
    session = get_session()
    naive = datetime.datetime(2012, 3, 28, 9, 21, 34, 638972)
    aware = datetime.datetime(2012, 3, 28, 18, 21, 34, 638972,
                              tzinfo=FixedOffset(540))
    session.set(key('test_types_datetime'), naive, DateTime)
    dt = session.get(key('test_types_datetime'), DateTime)
    assert dt == naive
    session.set(key('test_types_datetime'), aware, DateTime)
    dt = session.get(key('test_types_datetime'), DateTime)
    assert dt.tzinfo is None
    assert dt == aware.replace(tzinfo=None)
    with raises(TypeError):
        session.set(key('test_types_datetime'), 1234, DateTime)
    session.set(key('test_types_datetime'), '1988-08-04', ByteString)
    with raises(ValueError):
        session.get(key('test_types_datetime'), DateTime)

