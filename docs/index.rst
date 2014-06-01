Sider
=====

.. image:: https://badge.fury.io/py/Sider.svg?
   :target: https://pypi.python.org/pypi/Sider
   :alt: Latest PyPI version

Sider is a persistent object library based on Redis_.  This is heavily under
development currently, but you can check the :doc:`future roadmap <roadmap>`
if you want.

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

   $ pip install Sider
   $ python -m sider.version
   0.2.0

What was the name 'Sider' originated from?:

.. sourcecode:: pycon

   >>> 'redis'[::-1]
   'sider'

.. _PyPI: https://pypi.python.org/pypi/Sider
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

   examples
   doc
   todo
   roadmap
   changes


Open source
-----------

.. image:: https://travis-ci.org/dahlia/sider.svg?branch=master
   :target: https://travis-ci.org/dahlia/sider
   :alt: Build Status

.. image:: https://img.shields.io/coveralls/dahlia/sider.svg?
   :target: https://coveralls.io/r/dahlia/sider
   :alt: Coverage Status

Sider is an open source software written in `Hong Minhee`__.  The source code
is distributed under `MIT license`__ and you can find it at `GitHub
repository`__.  Check out now:

.. sourcecode:: console

   $ git clone git://github.com/dahlia/sider.git

If you find a bug, report it to `the issue tracker`__ or send pull requests.

__ http://dahlia.kr/
__ http://minhee.mit-license.org/
__ https://github.com/dahlia/sider
__ https://github.com/dahlia/sider/issues


Community
---------

Sider has the official IRC channel on freenode: irc://chat.freenode.net/sider


Indices and tables
------------------

- :ref:`genindex`
- :ref:`modindex`
- :ref:`search`

