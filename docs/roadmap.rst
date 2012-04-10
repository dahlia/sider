Roadmap
=======

Sider is planning to provide a lot of things able to be done with Redis.
It will be a long-running project, and planned features have their
priority.


Version 0.2
-----------

Transactions
   The key feature Sider 0.2 ships will be a transaction support.
   It has been being developed in the branch :branch`transaction`.

Sorted sets (:class:`sider.sortedset`)
   Redis sorted sets will be mapped to an interface like
   :class:`collections.Counter` but with slightly different behavior.
   The branch name for this will be :branch:`sortedset`.

Tuple type (:class:`sider.types.Tuple`)
   It could be used for storing ad-hoc composite types.
   The branch name for this will be :branch:`types-tuple`.


Version 0.3
-----------

Entity mapping
   The main feature Sider 0.3 ships will be an entity mapper inspired by
   SQLAlchemy's manual mapper.  In this version, entity mapper doesn't
   support any declarative interface yet.

   It has been being developed in the branch :branch:`entity-mapping`.

Channels (:mod:`sider.channel`)
   Using Redis' pub/sub channels you will be able to use Redis
   as your simple message queue.

   The branch name for this will be :branch:`channel`.

Extension namespace (:mod:`sider.ext`)
   User-contributed modules can be plugged inside the namespace
   :mod:`sider.ext`.  If you write an extension module for Sider
   and name it :mod:`sider_something` it will be imported by
   :mod:`sider.ext.something`.

   It has been being developed in the branch :branch:`ext`.


