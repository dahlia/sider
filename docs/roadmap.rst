Roadmap
=======

Sider is planning to provide a lot of things able to be done with Redis.
It will be a long-running project, and planned features have their
priority.


Version 0.3
-----------

Entity mapping (:mod:`sider.entity`)
   The main feature Sider 0.3 ships will be an entity mapper inspired by
   SQLAlchemy's manual mapper.  In this version, entity mapper doesn't
   support any declarative interface yet.

   It has been being developed in the branch :branch:`entity-mapping`.

Key templates (:mod:`sider.key`)
   You can organize keys by grouped values instead of raw vanilla string
   keys.

   The branch name for this will be :branch:`key`.

Channels (:mod:`sider.channel`)
   By using Redis' pub/sub channels you will be able to use Redis
   as your simple message queue.

   The branch name for this will be :branch:`channel`.

Extension namespace (:mod:`sider.ext`)
   User-contributed modules can be plugged inside the namespace
   :mod:`sider.ext`.  If you write an extension module for Sider
   and name it :mod:`sider_something` it will be imported by
   :mod:`sider.ext.something`.

   It has been being developed in the branch :branch:`ext`.


Version 0.4
-----------

Declarative entity mapper (:mod:`sider.entity.declarative`)
   Inspired by SQLAlchemy's declarative mapper, by using metaclasses,
   Sider will provide the easier mapping interface to use built on
   top of the manual mapper.

   It will be developed in the branch :branch:`entity-mapping`.

Indices (:mod:`sider.entity.index`)
   While Redis hashes don't have any indices Sider's entity mapper
   will provide indices for arbitrary expressions by generating
   materialized views and you can search entities by indexed fields.

   It will be developed in the branch :branch:`entity-index`.

Simple distributed task queue (:mod:`sider.ext.task`)
   By using :mod:`sider.channel` Sider will offer the simple distributed
   task queue.  It will have very subset features of Celery (while Celery
   supports various AMQP implementations other than Redis e.g. RabbitMQ).

   It will be developed in the branch :branch:`ext-task`.


Any other features?
-------------------

Isn't there the feature what you're looking for?  So write__ the feature
request in our `issue tracker`__.

__ https://github.com/dahlia/sider/issues/new
__ https://github.com/dahlia/sider/issues

