""":mod:`sider.session` --- Sessions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What sessions mainly do are `identity map`__ and `unit of work`__.

__ http://martinfowler.com/eaaCatalog/identityMap.html
__ http://martinfowler.com/eaaCatalog/unitOfWork.html

"""
from redis.client import Redis
from .types import Value, ByteString


class Session(object):
    """Session is an object which manages Python objects that represent Redis
    values e.g. lists, sets, hashes.  It maintains identity maps between
    Redis values and Python objects, and deals with transactions.

    :param client: the Redis client
    :type client: :class:`redis.client.Redis`

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

    def get(self, key, value_type=ByteString):
        """Loads the value from the ``key``.
        If ``value_type`` is present the value will be treated as it,
        or :class:`~sider.types.ByteString` by default.

        :param key: the Redis key to load
        :type key: :class:`str`
        :param value_type: the type of the value to load.  default is
                           :class:`~sider.types.ByteString`
        :type value_type: :class:`~sider.types.Value`, :class:`type`
        :returns: the loaded value

        """
        value_type = Value.ensure_value_type(value_type,
                                             parameter='value_type')
        return value_type.load_value(self, key)

    def set(self, key, value, value_type=ByteString):
        """Stores the ``value`` into the ``key``.
        If ``value_type`` is present the value will be treated as it,
        or :class:`~sider.types.ByteString` by default.

        :param key: the Redis key to save the value into
        :type key: :class:`str`
        :param value: the value to be saved
        :param value_type: the type of the ``value``.  default is
                           :class:`~sider.types.ByteString`
        :type value_type: :class:`~sider.types.Value`, :class:`type`
        :returns: the Python representation of the saved value.
                  it is equivalent to the given ``value`` but
                  may not equal nor the same to

        """
        value_type = Value.ensure_value_type(value_type,
                                             parameter='value_type')
        return value_type.save_value(self, key, value)

