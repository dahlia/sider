# -*- coding: utf-8 -*-
import datetime
import uuid
from pytest import raises
from .env import key
from .env import session
from sider import types
from sider.types import (Boolean, ByteString, Date, DateTime, Integer, String,
                         Tuple, TZDateTime, UUID)
from sider.datetime import FixedOffset


try:
    bytes_t = bytes
except NameError:
    bytes_t = str


def test_encoding():
    integer_type = types.Integer()
    bytestring_type = types.ByteString()
    unicode_type = types.UnicodeString()
    boolean_type = types.Boolean()
    tuple_type = types.Tuple(types.Integer, types.UnicodeString)
    date_type = types.Date()
    datetime_type = types.DateTime()
    tz_datetime_type = types.TZDateTime()
    time_type = types.Time()
    tz_time_type = types.TZTime()
    timedelta_type = types.TimeDelta()
    assert type(integer_type.encode(42)) == bytes_t
    assert type(bytestring_type.encode(b'annyeong')) == bytes_t
    assert type(unicode_type.encode(u'안녕')) == bytes_t
    assert type(boolean_type.encode(True)) == bytes_t
    assert type(tuple_type.encode((1, u'2'))) == bytes_t
    assert type(date_type.encode(datetime.date(1988, 5, 28))) == bytes_t
    assert type(datetime_type.encode(datetime.datetime.now())) == bytes_t
    tzdt = datetime.datetime(2013, 3, 8, 17, 2, 9,
                             tzinfo=FixedOffset(540))
    assert type(tz_datetime_type.encode(tzdt)) == bytes_t
    assert type(time_type.encode(datetime.time(7, 21, 39))) == bytes_t
    tzt = datetime.time(13, 0, 42, tzinfo=FixedOffset(360))
    assert type(tz_time_type.encode(tzt)) == bytes_t
    assert type(timedelta_type.encode(datetime.timedelta(days=1))) == bytes_t


def test_boolean(session):
    session.set(key(u'test_types_boolean_t'), True, Boolean)
    assert session.get(key(u'test_types_boolean_t'), Boolean) is True
    session.set(key(u'test_types_boolean_t2'), 2, Boolean)
    assert session.get(key(u'test_types_boolean_t2'), Boolean) is True
    session.set(key(u'test_types_boolean_f'), False, Boolean)
    assert session.get(key(u'test_types_boolean_f'), Boolean) is False


def test_date(session):
    date = session.set(key(u'test_types_date'),
                       datetime.date(1988, 8, 4),
                       Date)
    assert date == datetime.date(1988, 8, 4)
    with raises(TypeError):
        session.set(key(u'test_types_date'), 1234, Date)
    session.set(key(u'test_types_date'), b'19880804', ByteString)
    with raises(ValueError):
        session.get(key(u'test_types_date'), Date)


def test_datetime(session):
    naive = datetime.datetime(2012, 3, 28, 9, 21, 34, 638972)
    aware = datetime.datetime(2012, 3, 28, 18, 21, 34, 638972,
                              tzinfo=FixedOffset(540))
    session.set(key(u'test_types_datetime'), naive, DateTime)
    dt = session.get(key(u'test_types_datetime'), DateTime)
    assert dt == naive
    session.set(key(u'test_types_datetime'), aware, DateTime)
    dt = session.get(key(u'test_types_datetime'), DateTime)
    assert dt.tzinfo is None
    assert dt == aware.replace(tzinfo=None)
    with raises(TypeError):
        session.set(key(u'test_types_datetime'), 1234, DateTime)
    session.set(key(u'test_types_datetime'), b'1988-08-04', ByteString)
    with raises(ValueError):
        session.get(key(u'test_types_datetime'), DateTime)


def test_tzdatetime(session):
    aware = datetime.datetime(2012, 3, 28, 18, 21, 34, 638972,
                              tzinfo=FixedOffset(540))
    session.set(key(u'test_types_tzdatetime'), aware, TZDateTime)
    dt = session.get(key(u'test_types_tzdatetime'), TZDateTime)
    assert dt.tzinfo is not None
    assert dt == aware
    with raises(TypeError):
        session.set(key(u'test_types_tzdatetime'), 1234, TZDateTime)
    naive = datetime.datetime(2012, 3, 28, 9, 21, 34, 638972)
    with raises(ValueError):
        session.set(key(u'test_types_tzdatetime'), naive, TZDateTime)
    session.set(key(u'test_types_tzdatetime'), b'1988-08-04', ByteString)
    with raises(ValueError):
        session.get(key(u'test_types_tzdatetime'), TZDateTime)


def test_uuid(session):
    uuid_v4 = uuid.UUID('ed386d46-fbe2-4cbc-98ab-72e90436b4a3')
    session.set(key('test_types_uuid'), uuid_v4, UUID)
    u = session.get(key('test_types_uuid'), UUID)
    assert u == uuid_v4
    assert u.version == 4
    with raises(TypeError):
        session.set(key('test_types_uuid'),
                    22474335462895695114168873682703774849, UUID)
    session.set(key('test_types_uuid'),
                b'\x11\xea.X\x97bG\xf3\xa31\xf2\xfaY\x95\xb7m', ByteString)
    with raises(ValueError):
        session.get(key('test_types_uuid'), UUID)


def test_tuple(session):
    int_str_int = Tuple(Integer, String, Integer)
    tupl = (123, 'abc\ndef', 456,)
    encoded = int_str_int.encode(tupl)
    decoded = int_str_int.decode(encoded)
    assert decoded == tupl
    session.set(key('test_types_tuple'), tupl, int_str_int)
    t = session.get(key('test_types_tuple'), int_str_int)
    assert t == tupl
