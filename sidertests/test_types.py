import datetime
from pytest import raises
from .env import key
from .env import session
from sider.types import Boolean, ByteString, Date, DateTime, TZDateTime
from sider.datetime import FixedOffset


def test_boolean(session):
    session.set(key('test_types_boolean_t'), True, Boolean)
    assert session.get(key('test_types_boolean_t'), Boolean) is True
    session.set(key('test_types_boolean_t2'), 2, Boolean)
    assert session.get(key('test_types_boolean_t2'), Boolean) is True
    session.set(key('test_types_boolean_f'), False, Boolean)
    assert session.get(key('test_types_boolean_f'), Boolean) is False


def test_date(session):
    date = session.set(key('test_types_date'), datetime.date(1988, 8, 4), Date)
    assert date == datetime.date(1988, 8, 4)
    with raises(TypeError):
        session.set(key('test_types_date'), 1234, Date)
    session.set(key('test_types_date'), '19880804', ByteString)
    with raises(ValueError):
        session.get(key('test_types_date'), Date)


def test_datetime(session):
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


def test_tzdatetime(session):
    aware = datetime.datetime(2012, 3, 28, 18, 21, 34, 638972,
                              tzinfo=FixedOffset(540))
    session.set(key('test_types_tzdatetime'), aware, TZDateTime)
    dt = session.get(key('test_types_tzdatetime'), TZDateTime)
    assert dt.tzinfo is not None
    assert dt == aware
    with raises(TypeError):
        session.set(key('test_types_tzdatetime'), 1234, TZDateTime)
    naive = datetime.datetime(2012, 3, 28, 9, 21, 34, 638972)
    with raises(ValueError):
        session.set(key('test_types_tzdatetime'), naive, TZDateTime)
    session.set(key('test_types_tzdatetime'), '1988-08-04', ByteString)
    with raises(ValueError):
        session.get(key('test_types_tzdatetime'), TZDateTime)
