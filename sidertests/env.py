import os
import datetime
from redis.client import Redis
from sider.session import Session


def get_client():
    host = os.environ.get('SIDERTEST_HOST', 'localhost')
    port = int(os.environ.get('SIDERTEST_PORT', 6379))
    db = int(os.environ.get('SIDERTEST_DB', 0))
    return Redis(host=host, port=port, db=db)


def get_session():
    return Session(get_client())


prefix = 'sidertests_{0:%Y%m%d%H%M%S%f}_'.format(datetime.datetime.now())


def key(key):
    global prefix
    return prefix + str(key)

