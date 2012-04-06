import threading
try:
    import greenlet
except ImportError:
    greenlet = None
from attest import Tests, assert_hook, raises
from sider.threadlocal import get_ident


tests = Tests()


def thread_test(generator, args1=(), args2=()):
    def test(g, *args):
        g.next()
        for arg in args:
            try:
                g.send(arg)
            except StopIteration:
                break
    t1 = threading.Thread(target=test, args=(generator(),) + args1)
    t2 = threading.Thread(target=test, args=(generator(),) + args2)
    t1.start()
    t2.start()
    t1.join()
    t2.join()


if greenlet:
    def coro_test(generator, args1=(), args2=()):
        def test(g, (cc, next_args), *args):
            g.next()
            for arg in args:
                try:
                    g.send(arg)
                except StopIteration:
                    break
                finally:
                    if cc is not None:
                        cc.switch(*next_args)
        c1 = greenlet.greenlet(test)
        c2 = greenlet.greenlet(test)
        c1.switch(generator(),
                  (c2, (generator(), (c1, ())) + args2),
                  *args1)
else:
    def coro_test(*a, **k):
        pass # skip


@tests.test
def test_get_ident():
    result = [None, None]
    local = {}
    def run():
        value = yield
        local[get_ident()] = value
        result_idx = yield
        result[result_idx] = local.setdefault(get_ident())
    thread_test(run, (123, 0), (456, 1))
    assert result == [123, 456]
    if greenlet:
        result = [None, None]
        coro_test(run, (123, 0), (456, 1))
        assert result == [123, 456]

