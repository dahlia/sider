import doctest
from attest import Tests
from . import list


tests = Tests()
tests.register(list.tests)


@tests.test
def doctest_datetime():
    import sider.datetime
    assert 0 == doctest.testmod(sider.datetime)[0]

