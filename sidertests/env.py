import os
import datetime
from redis.client import StrictRedis
from sider.session import Session
from sider.types import Integer


def get_client(cls=StrictRedis):
    host = os.environ.get('SIDERTEST_HOST', 'localhost')
    port = int(os.environ.get('SIDERTEST_PORT', 6379))
    db = int(os.environ.get('SIDERTEST_DB', 0))
    return cls(host=host, port=port, db=db)


def get_session():
    return Session(get_client())


prefix = 'sidertests_{0:%Y%m%d%H%M%S%f}_'.format(datetime.datetime.now())


def key(key):
    global prefix
    return prefix + str(key)


def init_session():
    client = get_client()
    try:
        session = Session(client)
        yield session
    finally:
        #: .. note::
        #:
        #:    Using ``FLUSHALL`` command is more easier and faster, but it's
        #:    also harmful because it flushes all data in the selected db.
        #:
        #:    However if it is assumed that there is no meaningful data in the
        #:    db, ``client.flushall()`` can be used safely and the testing
        #:    speed will be improved.
        used_keys = client.keys(prefix + '*')
        if used_keys:
            client.delete(*used_keys)


class NInt(Integer):
    """Saves integers as its negative number.  Testing purpose."""

    def encode(self, value):
        if not isinstance(value, (int, long)):
            raise TypeError('expected an integer, not {0!r}; something went '
                            'wrong!'.format(value))
        return Integer.encode(self, -value + 6)

    def decode(self, bulk):
        return -(Integer.decode(self, bulk) - 6)

