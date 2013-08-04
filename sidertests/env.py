import os
import datetime
import numbers
import pytest
from redis.client import StrictRedis, ConnectionError
from sider.session import Session
from sider.types import Integer


def get_client(cls=StrictRedis):
    host = os.environ.get('SIDERTEST_HOST', 'localhost')
    port = int(os.environ.get('SIDERTEST_PORT', 6379))
    db = int(os.environ.get('SIDERTEST_DB', 0))
    try:
        client = cls(host=host, port=port, db=db)
        # To connect on the server forcibly,
        # send a ping explicitly at this line.
        client.ping()
        return client
    except ConnectionError as e:
        pytest.fail(str(e), pytrace=False)


def get_session(client=None):
    if client is None:
        client = get_client()
    session = Session(client)
    session.verbose_transaction_error = True
    return session


prefix = 'sidertests_{0:%Y%m%d%H%M%S%f}_'.format(datetime.datetime.now())


def key(key):
    global prefix
    return prefix + str(key)


@pytest.fixture
def session(request):
    client = get_client()
    session = get_session(client)

    @request.addfinalizer
    def fin():
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
    return session


class NInt(Integer):
    """Saves integers as its negative number.  Testing purpose."""

    def encode(self, value):
        if not isinstance(value, numbers.Integral):
            raise TypeError('expected an integer, not {0!r}; something went '
                            'wrong!'.format(value))
        return Integer.encode(self, -value + 6)

    def decode(self, bulk):
        return -(Integer.decode(self, bulk) - 6)
