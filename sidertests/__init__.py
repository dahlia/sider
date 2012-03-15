import doctest
from attest import Tests


tests = Tests()


@tests.test
def doctest_datetime():
    import sider.datetime
    assert 0 == doctest.testmod(sider.datetime)[0]

