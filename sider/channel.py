""":mod:`sider.channel` --- Pub/Sub channels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. seealso::

   `Redis Pub/Sub <http://redis.io/topics/pubsub>`_
       The Redis documentation that explains about its publish/subscribe
       messaging system.

"""


class Message(tuple):
    """The :class:`tuple` subtype to represent pushed messages.
    It is a kind of quadruple (4-:class:`tuple`): (:attr:`kind`,
    :attr:`pattern`, :attr:`channel`, :attr:`value`) in order.
    So, you can access each field by indices, attributes or
    tuple unpacking as well.  ::

        assert isinstance(message, Message)

        kind = message[0]
        pattern = message[1]
        channel = message[2]
        value = message.value

        kind = message.kind
        pattern = message.pattern
        channel = message.channel
        value = message.value

        kind, pattern, channel, value = message

    :param kind: the :attr:`kind` of message.  should be one of
                 3 strings: ``'subscribe'``, ``'unsubscribe'`` or
                 ``'message'``
    :type kind: :class:`basestring`
    :param pattern: the :attr:`pattern` we are subscribed to
    :type channel: :class:`basestring`
    :param channel: the :attr:`channel` we are subscribed to
                    or the message was pushed to
    :type channel: :class:`basestring`
    :param value: the :attr:`value` of the message, or the number
                  of channels we are currently subscribed to

    """

    __slots__ = () 

    def __new__(cls, kind, pattern, channel, value):
        return tuple.__new__(cls, (kind, pattern, channel, value)) 

    def __getnewargs__(self):
        return tuple(self) 

    @property
    def kind(self):
        """(:class:`basestring`) The :attr:`kind` attribute which
        is the first field can be one of these strings:

        ``'subscribe'``
           It means that we successfully subscribed to the
           :attr:`channel` given as the third field in the reply.

           The fourth field :attr:`value` represents the number of
           channels we are currently subscribed to.

        ``'unsubscribe'``
           It means that we successfully unsubscribed from
           the :attr:`channel` given as third field in the reply.

           The fourth field :attr:`value` represents the number of
           channels we are currently subscribed to.

           When the last field is zero, we are no longer subscribed
           to any channel, and the client can issue any kind of Redis
           command as we are outside the pub/sub state.

        ``'message'``
           It is a message received as result of a :redis:`PUBLISH`
           command issued by another client.  The third field
           :attr:`channel` is the name of the originating channel,
           and the fourth field :attr:`value` is the actual message
           payload.

        """
        return self[0]

    @property
    def pattern(self):
        """(:class:`basestring`) The pattern we are subscribing to."""
        return self[1]

    @property
    def channel(self):
        """(:class:`basestring`) The channel we are subscribing to
        or the message was pushed to.

        """
        return self[2]

    @property
    def value(self):
        """The value of the message if :attr:`kind` is ``'message'``,
        or the number of channels we are currently subscribing to
        when :attr:`kind` is ``'subscribe'`` or ``'unsubscribe'``.

        """
        return self[3]

    def __repr__(self):
        cls = type(self)
        fmt = '{0}.{1}(kind={2!r}, pattern={3!r}, channel={4!r}, value={5!r})'
        return fmt.format(cls.__module__, cls.__name__, *self)

