Design memo
===========

Directions
----------

- Do not reinvent the wheel.  Use redis-py for connection pooling.
  It already is mature.
- Don't be implicit.  Hashes aren't entities.  Hash keys aren't fields.
  Connections aren't sessions.


Example
-------

Schema

::

    from sider.entity import Entity, Field
    from sider.types import UnicodeString, Date, TZDateTime
    from sider.datetime import now
    from .password import Password


    class User(Entity):
        """User entity."""

        login = Field(UnicodeString, required=True, key=True)
        password = Field(UnicodeString, required=True)
        name = Field(UnicodeString, required=True)
        url = Field(UnicodeString, unique=True)
        dob = Field(Date)
        created_at = Field(TZDateTime, required=True, default=now)

        @login.before_set
        def login(self, value):
            value = value.strip().lower()
            if 2 < len(value) < 50:
                return value
            raise ValueError('invalid login')

        @password.before_set
        def password(self, value):
            return Password.hash(self, value)

        @password.after_get
        def password(self, value):
            return Password(self, value)

        def __unicode__(self):
            return getattr(self, 'user', None) or u''

Query

.. sourcecode:: pycon

   >>> from redis.client import StrictRedis
   >>> from sider.session import Session
   >>> from myapp.user import User
   >>> session = Session(StrictRedis(host='127.0.0.1', port=6379, db=0))
   >>> user = session.get(User, 'hongminhee')
   >>> user
   <myapp.user.User 'users:hongminhee'>
   >>> user.password
   <myapp.password.Password user='hongminhee'>

