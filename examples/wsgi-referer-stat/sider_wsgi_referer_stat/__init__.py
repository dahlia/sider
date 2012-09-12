r""":mod:`sider.ext.wsgi_referer_stat` --- Collecting referers using sorted sets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This tutorial will show you a basic example using sorted sets.
We will build a small WSGI middleware that simply collects all
:mailheader:`Referer`\s of the given WSGI web application.


WSGI and middlewares
--------------------

WSGI is a standard interface between web servers and Python web
applications or frameworks to promote web application portability
across a variety of web servers.  (If you are from Java, think servlet.
If you are from Ruby, think Rack.)

WSGI applications can be deployed into WSGI containers (server
implementations).  There are a lot of production-ready WSGI
containers.  Some of these are super fast, and some of others
are very reliable.  Check `Green Unicorn`_, uWSGI_, mod_wsgi_,
and so forth.

WSGI middleware is somewhat like decorator pattern for WSGI
applications.  Usually they are implemented using nested
higher-order functions or classes with :meth:`~object.__call__()`
special method.

.. seealso::

   To learn more details about WSGI, read :pep:`333` and other related
   resources.  This tutorial doesn't deal with WSGI.

   :pep:`333` --- Python Web Server Gateway Interface v1.0
      This document specifies a proposed standard interface between
      web servers and Python web applications or frameworks, to promote
      web application portability across a variety of web servers.

   `Getting Started with WSGI`__ by Armin Ronacher
      Armin Ronacher, the author of Flask_, Werkzeug_ and Jinja_,
      wrote this WSGI tutorial.

   `A Do-It-Yourself Framework`__ by Ian Bicking
      Ian Bicking, the author of Paste_, WebOb_, lxml.html_ and
      FormEncode_, explains about WSGI apps and middlewares.

.. _Green Unicorn: http://gunicorn.org/
.. _uWSGI: http://projects.unbit.it/uwsgi/
.. _mod_wsgi: http://code.google.com/p/modwsgi/
__ http://lucumr.pocoo.org/2007/5/21/getting-started-with-wsgi/
.. _Flask: http://flask.pocoo.org/
.. _Werkzeug: http://werkzeug.pocoo.org/
.. _Jinja: http://jinja.pocoo.org/
__ http://pythonpaste.org/do-it-yourself-framework.html
.. _Paste: http://pythonpaste.org/
.. _WebOb: http://www.webob.org/
.. _lxml.html: http://lxml.de/lxmlhtml.html
.. _FormEncode: http://www.formencode.org/


Simple idea
-----------

The simple idea we'll implement here is to collect all :mailheader:`Referer`
and store it into a persistent storage.  We will use Redis as its persistent
store.  We want to increment the count for each :mailheader:`Referer`.

Stored data will be like:

==================================  =====
Referer                             Count
==================================  =====
http://dahlia.kr/                   1
https://github.com/dahlia/sider     3
https://twitter.com/hongminhee      6
==================================  =====

We could use a hash here, but sorted set seems more suitable.
Sorted sets are a data structure provided by Redis that is basically
a set but able to represent duplications as its scores (:redis:`ZINCRBY`).

We can list a sorted set in asceding (:redis:`ZRANGE`) or
descending order (:redis:`ZREVRANGE`) as well.

.. seealso::

    `Redis Data Types`__
       The Redis documentation that explains about its data
       types: strings, lists, sets, sorted sets and hashes.

__ http://redis.io/topics/data-types


Prototyping with using in-memory dictionary
-------------------------------------------

First of all, we can implement a proof-of-concept prototype without Redis.
Python has no sorted sets, so we will use :class:`dict` instead. ::

    class RefererStatMiddleware(object):
        '''A simple WSGI middleware that collects :mailheader:`Referer`
        headers.

        '''

        def __init__(self, application):
            assert callable(application)
            self.application = application
            self.referer_set = {}

        def __call__(self, environ, start_response):
            try:
                referer = environ['HTTP_REFERER']
            except KeyError:
                pass
            else:
                try:
                    self.referer_set[referer] += 1
                except KeyError:
                    self.referer_set[referer] = 1
            return self.application(environ, start_response)

It has some problems yet.  What are that problems?

1. WSGI applications can be deployed into multiple server nodes,
   or forked to multiple processes as well.  That means:
   :attr:`RefererStatMiddleware.referer_set` attribute can be
   split and not shared.

2. Increments of duplication counts aren't atomic.

3. Data will be lost when server process is terminated.

We can solve those problems by using Redis sorted sets instead of
Python in-memorty :class:`dict`.


Sider and persistent objects
----------------------------

It's a simple job, so we can deal with Redis commands by our hands.
However it's a tutrial example of Sider.  :-)  We will use Sider's
sorted set abstraction here instead.  It's more abstracted away and
easier to use!

Before touch our middleware code, the following session in Python
interactive shell can make you understand basic of how to use
Sider:

>>> from redis.client import StrictRedis
>>> from sider.session import Session
>>> from sider.types import SortedSet
>>> session = Session(StrictRedis())
>>> my_sorted_set = session.get('my_sorted_set', SortedSet)
>>> my_sorted_set
<sider.sortedset.SortedSet ('my_sorted_set') {}>

.. note::

   Did you face :exc:`~exceptions.ImportError`?

   >>> from redis.client import StrictRedis
   Traceback (most recent call last):
     File "<console>", line 1, in <module>
   ImportError: No module named redis

   You probably didn't install Python redis_ client library.
   You can install it through :program:`pip`:

   .. sourcecode:: console

      $ pip install redis

   Or :program:`easy_install`:

   .. sourcecode:: console

      $ easy_install redis

Okay, here's an empty set: ``my_sorted_set``.  Let's add something to it.

>>> my_sorted_set
<sider.sortedset.SortedSet ('my_sorted_set') {}>
>>> my_sorted_set.add('http://dahlia.kr/')  # ZINCRBY
>>> my_sorted_set
<sider.sortedset.SortedSet ('my_sorted_set') {'http://dahlia.kr/'}>

Unlike Python's in-memory :class:`set` or :class:`dict`,
it's a persistent object.  In other words, ``my_sorted_set``
still contains ``'http://dahlia.kr/'`` even if you quit this session of
Python interactive shell.  Try yourself: type :data:`exit() <exit>`
to quit the session and enter :program:`python` again.  And then...

>>> my_sorted_set
Traceback (most recent call last):
  File "<console>", line 1, in <module>
NameError: global name 'my_sorted_set' is not defined

I didn't lie!  You need to load the Sider session first.

>>> from redis.client import StrictRedis
>>> from sider.session import Session
>>> from sider.types import SortedSet
>>> client = StrictRedis()
>>> session = Session(client)
>>> my_sorted_set = session.get('my_sorted_set', SortedSet)

Then:

>>> my_sorted_set
<sider.sortedset.SortedSet ('my_sorted_set') {'http://dahlia.kr/'}>

Yeah!

Note that the following line:

>>> client = StrictRedis()

tries to connect to Redis server on localhost:6379 by default.
There are ``host`` and ``port`` parameters to configure it.

>>> client = StrictRedis(host='localhost', port=6379)

.. _redis: https://github.com/andymccurdy/redis-py


Sorted sets
-----------

You can :meth:`~sider.sortedset.SortedSet.update()` multiple values at a time:

>>> my_sorted_set.update(['https://github.com/dahlia/sider',
...                       'https://twitter.com/hongminhee'])  # ZINCRBY
>>> my_sorted_set
<sider.sortedset.SortedSet ('my_sorted_set')
 {'https://github.com/dahlia/sider', 'https://twitter.com/hongminhee',
  'http://dahlia.kr/'}>
>>> my_sorted_set.update(['http://dahlia.kr/',
...                       'https://twitter.com/hongminhee'])  # ZINCRBY
>>> my_sorted_set
<sider.sortedset.SortedSet ('my_sorted_set')
 {'https://github.com/dahlia/sider', 'https://twitter.com/hongminhee': 2.0,
  'http://dahlia.kr/': 2.0}>
>>> my_sorted_set['http://dahlia.kr/']  # ZSCORE
2.0
>>> my_sorted_set.add('http://dahlia.kr/')
>>> my_sorted_set['http://dahlia.kr/']  # ZSCORE
3.0

As you can see, doubly added members get double scores.  This property is
what we will use in the middleware.

You can list values and these scores the sorted set contains.
Similar to :class:`dict` there's :meth:`~sider.sortedset.SortedSet.items()`
method.

>>> my_sorted_set.items()  # ZRANGE
[('https://github.com/dahlia/sider', 1.0),
 ('https://twitter.com/hongminhee', 2.0),
 ('http://dahlia.kr/', 2.0)]
>>> my_sorted_set.items(reverse=True)  # ZREVRANGE
[('http://dahlia.kr/', 2.0),
 ('https://twitter.com/hongminhee', 2.0),
 ('https://github.com/dahlia/sider', 1.0)]

There are other many features to :class:`~sider.sortedset.SortedSet` type,
but it's all we need to know to implement the middleware.  So we stop
introduction of the type to step forward.


Replace :class:`dict` with :class:`~sider.sortedset.SortedSet`
--------------------------------------------------------------

To replace :class:`dict` with :class:`~sider.sortedset.SortedSet`,
look :meth:`RefererStatMiddleware.__init__()` method first::

    def __init__(self, application):
        self.application = application
        self.referer_set = {}

.. note::

   The following codes implictly assumes that it imports::

       from redis.client import StrictRedis
       from sider.session import Session
       from sider.types import SortedSet

The above code can be easily changed to:

::

    def __init__(self, application):
        assert callable(application)
        self.application = application
        client = StrictRedis()
        session = Session(client)
        self.referer_set = session.get('wsgi_referer_set', SortedSet)

It should be more configurable by users.  Redis key is currently hard-coded
as ``wsgi_referer_set``.  It can be parameterized, right? ::

    def __init__(self, set_key, application):
        assert callable(application)
        self.application = application
        client = StrictRedis()
        session = Session(client)
        self.referer_set = session.get(str(set_key), SortedSet)

It still lacks configurability.  Users can't set address of Redis server
to connect.  Parameterize ``session`` as well::

    def __init__(self, session, set_key, application):
        assert isinstance(session, Session)
        assert callable(application)
        self.application = application
        self.referer_set = session.get(str(set_key), SortedSet)

Okay, it's enough flexible to environments.  Our first and third problems
have just solved.  Its data become shared and don't be split anymore.
No data loss even if process has terminated.

Next, we have to make increment atomic.  See a part of
:meth:`RefererStatMiddleware.__call__()` method::

    try:
        self.referer_set[referer] += 1
    except KeyError:
        self.referer_set[referer] = 1

Redis sorted set offers a simple atomic way to increase its score:
:redis:`ZINCRBY`.  Sider maps :redis:`ZINCRBY` command to
:meth:`SortedSet.add() <sider.sortedset.SortedSet.add>` method.
So, those lines can be replaced by the following line::

    self.referer_set.add(referer)

and it will be committed atomically.


Referer list page
-----------------

Lastly, let's add an additional page for listing collected referers.
This page simply shows you list of referers and counts.  Referers are
ordered by these counts (descendingly).

To deal with HTML this example will use Jinja_ template engine.
Its syntax is similar to Django template language, but more expressive.
You can install it through :program:`pip` or :program:`easy_install`:

.. sourcecode:: console

   $ pip install Jinja2  # or:
   $ easy_install Jinja2

Here is a HTML template code using Jinja:

.. sourcecode:: html+jinja

   <h1>Referer List</h1>
   <table>
     <thead>
       <tr>
         <th>URL</th>
         <th>Count</th>
       </tr>
     </thead>
     <tbody>
       {% for url, count in referers %}
         <tr>
           <th><a href="{{ url|escape }}" rel="noreferrer">
                 {{- url|escape }}</a></th>
           <td>{{ count|int }}</td>
         </tr>
       {% endfor %}
     </tbody>
   </table>

Save this template source to the file named :file:`templates/stat.html`.
Remember we used an undefined variable in the above template code:
``referers``.  So we have to pass this variable from the WSGI middleware code.

To load this template file, Jinja environment object has to be set in the web
application code.  Append the following lines to
:meth:`RefererStatMiddleware.__init__()` method::

    loader = PackageLoader(__name__)
    environment = Environment(loader=loader)

And then we now can load the template using :meth:`Environment.get_template()
<jinja2.Environment.get_template>` method.  Append the following line to
:meth:`RefererStatMiddleware.__init__()` method::

    self.template = environment.get_template('stat.html')

When :class:`RefererStatMiddleware` is initialized its template will be loaded
together.

Next, let's add a new :meth:`~RefererStatMiddleware.stat_application()` method,
going to serve the list page, into the middleware class.  This method has to
be a WSGI application as well::

    def stat_application(self, environ, start_response):
        content_type = 'text/html; charset=utf-8'
        start_response('200 OK', [('Content-Type', content_type)])
        referers = self.referer_set.items(reverse=True)
        return self.template.render(referers=referers).encode('utf-8'),

:meth:`Template.render() <jinja2.Template.render>` method takes variables to
pass as keywords and returns a rendered result as :class:`unicode` string.
We have passed the ``referers`` variable from this line.  Its value is made
by :class:`SortedSet.items() <sider.sortedset.SortedSet.items>` method with
``reverse=True`` option which means descending order.

To connect this modular WSGI application into the main application, we should
add the following conditional routine into the first of
:meth:`RefererStatMiddleware.__call__()` method::

    path = environ['PATH_INFO']
    if path == '/__stat__' or path.startswith('/__stat__/'):
        return self.stat_application(environ, start_response)

It will delegate its responsibility of responding to
:meth:`~RefererStatMiddleware.stat_application()` application if a request is
to the path ``/__stat__`` or its subpath.

Now go to ``/__stat__`` page and then your browser will show a table like
this:

    .. raw:: html

       <h1>Referer List</h1>
       <table>
         <thead>
           <tr>
             <th>URL</th>
             <th>Count</th>
           </tr>
         </thead>
         <tbody>
           <tr>
             <th><a href="https://twitter.com/hongminhee"
                    rel="noreferrer">https://twitter.com/hongminhee</a></th>
             <td>6</td>
           </tr>
           <tr>
             <th><a href="https://github.com/dahlia/sider"
                    rel="noreferrer">https://github.com/dahlia/sider</a></th>
             <td>3</td>
           </tr>
           <tr>
             <th><a href="http://dahlia.kr/"
                    rel="noreferrer">http://dahlia.kr/</a></th>
             <td>1</td>
           </tr>
         </tbody>
       </table>

Source code
-----------

The complete source code of this example can be found in
:file:`examples/wsgi-referer-stat/` directory of the repository.

https://github.com/dahlia/sider/tree/master/examples/wsgi-referer-stat

It's public domain, feel free!


Final API
---------

"""
from sider.session import Session
from sider.types import SortedSet
from jinja2 import Environment, PackageLoader


class RefererStatMiddleware(object):
    """A simple WSGI middleware that collects :mailheader:`Referer`
    headers and stores it into a Redis sorted set.

    You can see the list of referrers ordered by duplication count
    in ``/__stat__`` page (or you can configure the ``stat_path``
    argument).

    :param session: sider session object
    :type session: :class:`sider.session.Session`
    :param set_key: the key name of Redis sorted set
                    to store data
    :type set_key: :class:`basestring`
    :param application: wsgi app to wrap
    :type application: :class:`collections.Callable`
    :param stat_path: path to see the collected data.
                      default is ``'/__stat__'``.
                      if it's ``None`` the data cannot be accessed
                      from outside
    :type stat_path: :class:`basestring`

    """

    #: (:class:`sider.sortedset.SortedSet`) The set of collected
    #: :mailheader:`Referer` strings.
    referer_set = None

    def __init__(self, session, set_key, application, stat_path='/__stat__'):
        if not isinstance(session, Session):
            raise TypeError('session must be an instance of sider.session.'
                            'Session, not ' + repr(session))
        elif not callable(application):
            raise TypeError('application must be callable, not ' +
                            repr(application))
        self.session = session
        self.application = application
        self.referer_set = session.get(str(set_key), SortedSet)
        self.stat_path = stat_path
        loader = PackageLoader(__name__)
        environment = Environment(loader=loader)
        self.template = environment.get_template('stat.html')

    def stat_application(self, environ, start_response):
        """WSGI application that lists its collected referers."""
        content_type = 'text/html; charset=utf-8'
        start_response('200 OK', [('Content-Type', content_type)])
        referers = self.referer_set.items(reverse=True)
        stream = self.template.generate(referers=referers)
        for chunk in stream:
            yield chunk.encode('utf-8', 'ignore')

    def __call__(self, environ, start_response):
        if self.stat_path is not None:
            path = environ['PATH_INFO']
            if path == self.stat_path or path.startswith(self.stat_path + '/'):
                return self.stat_application(environ, start_response)
        try:
            referer = environ['HTTP_REFERER']
        except KeyError:
            pass
        else:
            self.referer_set.add(referer)
        return self.application(environ, start_response)

