import threading
try:
    import greenlet
except ImportError:
    greenlet = None
from attest import Tests, assert_hook, raises
from sider.threadlocal import get_ident


tests = Tests()


@tests.test
def get_ident_thread():
    result = [None, None]
    def test(value, result_idx):
        a = {get_ident(): value}
        result[result_idx] = a.get(get_ident())
    t1 = threading.Thread(target=test, args=(123, 0))
    t2 = threading.Thread(target=test, args=(456, 1))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    assert result == [123, 456]


if greenlet:
    @tests.test
    def get_ident_greenlet():
        result = [None, None]
        def test(value, result_idx, next_):
            a = {get_ident(): value}
            next_[0].switch(*next_[1:])
            result[result_idx] = a.get(get_ident())
            if next_:
                next_[0].switch(*next_[1:])
        g1 = greenlet.greenlet(test)
        g2 = greenlet.greenlet(test)
        g1.switch(123, 0, (g2, 456, 1, (g1, 123, 0, (g2, 456, 1, None))))
        assert result == [123, 456]

