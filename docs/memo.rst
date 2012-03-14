Design memo
===========

Schema

::

    from sider.entity import Entity, Field
    from sider.types import UnicodeString, Date, TZDateTime
    from sider.datetime import now
    from .password import Password


    class User(Entity):
        """User entity."""

        login = Field(UnicodeString, required=True)
        password = Field(UnicodeString, required=True)
        name = Field(UnicodeString, required=True)
        url = Field(UnicodeString)
        dob = Field(Date)
        created_at = Field(TZDateTime, required=True, default=now)
        __redis_key__ = 'users:{0.login}'

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

   >>> from sider.session import Session
   >>> session = Session('127.0.0.1', 6379)
   >>> user = session.get(User, 'hongminhee')
   >>> user
   <myapp.user.User 'users:hongminhee'>
   >>> user.password
   <myapp.password.Password user='hongminhee'>

