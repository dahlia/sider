Sider
=====

Sider is a persistent object library based on Redis_.  This is being planned
and heavily under development currently.

.. sourcecode:: pycon

   >>> from sider.types import Set, Integer
   >>> s = session.get('my_set', Set(Integer))
   >>> 3 in s  # SISMEMBER 3
   True
   >>> 4 in s  # SISMEMBER 4
   False
   >>> s2 = session.get('another_set', Set(Integer))
   >>> s & s2  # SINTER my_set another_set
   set([2, 3])
   >>> s
   <sider.set.Set {1, 2, 3}>
   >>> s2
   <sider.set.Set {-1, 0, 1, 2}>
   >>> session.get('my_int_key', Integer)
   1234

You can install it from PyPI_:

.. sourcecode:: console

   $ pip install Sider  # or
   $ easy_install Sider
   $ python -m sider.version
   0.1.2

What was the name 'Sider' originated from?:

.. sourcecode:: pycon

   >>> 'redis'[::-1]
   'sider'

.. _PyPI: http://pypi.python.org/pypi/Sider
.. _Redis: http://redis.io/


References
----------

.. toctree::
   :maxdepth: 2

   sider


Further reading
---------------

.. toctree::
   :maxdepth: 2

   doc
   memo
   todo
   roadmap
   changes


Open source
-----------

Sider is an open source software written in `Hong Minhee`__.  The source code
is distributed under `MIT license`__ and you can find it at `Bitbucket
repository`__.  Check out now:

.. sourcecode:: console

   $ hg clone https://bitbucket.org/dahlia/sider

If you find a bug, report it to `the issue tracker`__ or send pull requests.

__ http://dahlia.kr/
__ http://minhee.mit-license.org/
__ https://bitbucket.org/dahlia/sider
__ https://bitbucket.org/dahlia/sider/issues


Indices and tables
------------------

- :ref:`genindex`
- :ref:`modindex`
- :ref:`search`

