import doctest
import os
from attest import Tests
from . import (session, types, hash, list, set, sortedset, entity,
               transaction, threadlocal)


tests = Tests()
tests.register(session.tests)
tests.register(types.tests)
tests.register(hash.tests)
tests.register(list.tests)
tests.register(set.tests)
tests.register(sortedset.tests)
tests.register(entity.tests)
tests.register(transaction.tests)
tests.register(threadlocal.tests)


@tests.test
def doctest_types():
    from sider import types
    assert 0 == doctest.testmod(types)[0]


@tests.test
def doctest_datetime():
    from sider import datetime
    assert 0 == doctest.testmod(datetime)[0]


exttest_count = 0


@tests.test
def ext():
    from sider.ext import _exttest
    assert _exttest.ext_loaded == 'yes'
    assert exttest_count == 1
    from  sider import ext
    assert ext._exttest is _exttest
    try:
        import sider.ext._noexttest
    except ImportError as e:
        assert str(e) == "No module named 'sider.ext._noexttest'"
    else:
        assert False, 'it must raise ImportError'


@tests.test
def print_version():
    from sider.version import VERSION
    printed_version = os.popen('python -m sider.version').read().strip()
    assert printed_version == VERSION

