""":mod:`sider.session` --- Sessions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What sessions mainly do are `identity map`__ and `unit of work`__.

__ http://martinfowler.com/eaaCatalog/identityMap.html
__ http://martinfowler.com/eaaCatalog/unitOfWork.html

"""
import collections
from redis.client import Redis
from .list import List


class Session(object):
    """Session is an object which manages Python objects that represent Redis
    values e.g. lists, sets, hashes.  It maintains identity maps between
    Redis values and Python objects, and deals with transactions.

    :param client: the Redis client
    :type client: :class:`redis.client.Client`

    """

    def __init__(self, client):
        if not isinstance(client, Redis):
            raise TypeError('client must be a redis.client.Redis object, not '
                            + repr(client))
        self.client = client

    @property
    def server_version(self):
        """(:class:`str`) Redis server version string e.g. ``'2.2.11'``."""
        try:
            info = self._server_info
        except AttributeError:
            info = self.client.info()
            self._server_info = info
        return info['redis_version']

    @property
    def server_version_info(self):
        """(:class:`tuple`) Redis server version triple e.g. ``(2, 2, 11)``.
        You can compare versions using this property.

        """
        return tuple(int(v) for v in self.server_version.split('.'))

    def __getitem__(self, key):
        result = self.client.type(key).lower().strip()
        if result == 'list':
            return List(self, key)

    def __setitem__(self, key, value):
        pipe = self.client.pipeline()
        pipe.delete(key)
        if isinstance(value, collections.Sequence):
            if self.server_version_info < (2, 4, 0):
                for val in value:
                    pipe.rpush(key, val)
            else:
                pipe.rpush(key, *value)
        pipe.execute()

