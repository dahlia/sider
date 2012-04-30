Tests
=====

Testing tools
-------------

Sider uses Attest_ as its unit testing library.  It is very simple and
written in modern Python way.  You would probably be amazed if you find
its `assert hook`__ feature.

There's one more optional tool for testing: tox_.  It helps us to test
Sider on various Python implementations (e.g. PyPy, Stackless Python) and
versions (e.g. CPython 2.6, CPython 2.7) in one shot.

.. _Attest: http://packages.python.org/Attest/
__ http://packages.python.org/Attest/api/hook/
.. _tox: http://tox.readthedocs.org/


Running tests
-------------

You have to setup your Redis database to test.  Unit tests of Sider consist
of lots of destructive operations, so we highly recommend you to isolate
testing-purpose database from your other databases.

To run test, type the following command in the root of the source tree:

.. sourcecode:: console

   $ python setup.py test

It also installs Attest_ if you haven't installed it.

Testing script is aware of :ref:`some environment variables
<test-environment-variables>`.  You can set Redis server for testing.

.. sourcecode:: console

   $ SIDERTEST_HOST=localhost SIDERTEST_PORT=6379 python setup.py test

If you've installed :program:`tox`, use it:

.. sourcecode:: console

   $ tox

That's all!


.. _test-environment-variables:

Environment variables
---------------------

You can configure testing options by setting the following environment
variables.

:envvar:`SIDERTEST_HOST`
   The host of Redis server to be used for testing.  Default is ``localhost``.

:envvar:`SIDERTEST_PORT`
   The port of Redis server to be used for testing.  Default is 6379.

:envvar:`SIDERTEST_DB`
   The Redis database to be used for testing.  Default is 0.

