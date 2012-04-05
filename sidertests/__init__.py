import doctest
import os
from attest import Tests
from . import session, types, hash, list, set, threadlocal


tests = Tests()
tests.register(session.tests)
tests.register(types.tests)
tests.register(hash.tests)
tests.register(list.tests)
tests.register(set.tests)
tests.register(threadlocal.tests)


@tests.test
def doctest_types():
    from sider import types
    assert 0 == doctest.testmod(types)[0]


@tests.test
def doctest_datetime():
    from sider import datetime
    assert 0 == doctest.testmod(datetime)[0]


@tests.test
def print_version():
    from sider.version import VERSION
    printed_version = os.popen('python -m sider.version').read().strip()
    assert printed_version == VERSION

