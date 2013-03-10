import threading
try:
    import greenlet
except ImportError:
    greenlet = None
from sider.threadlocal import LocalDict, get_ident


def thread_test(generator, args1=(), args2=()):
    def test(g, *args):
        next(g)
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
        def test(g, v, *args):
            cc, next_args = v
            next(g)
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
        pass  # skip


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


def test_local_dict():
    local = LocalDict()
    result = [None, None]
    def run():
        value = yield
        local['a'] = value
        result_idx = yield
        result[result_idx] = (
            len(local), list(iter(local)), 'a' in local, 'b' in local,
            local['a'], local.copy(), local.get('a', 1), local.get('b', 2),
            'a' in local, 'b' in local, list(local.items()),
            list(local.iteritems()), list(local.iterkeys()),
            list(local.itervalues()), list(local.keys()), list(local.values()),
        )
    def assert_expects(result, value):
        assert result[0] == 1
        assert result[1] == ['a']
        assert result[2]
        assert not result[3]
        assert result[4] == value
        assert result[5] == {'a': value}
        assert result[6] == value
        assert result[7] == 2
        assert result[8]
        assert not result[9]
        assert result[10] == [('a', value)]
        assert result[11] == [('a', value)]
        assert result[12] == ['a']
        assert result[13] == [value]
        assert result[14] == ['a']
        assert result[15] == [value]
    thread_test(run, (123, 0), (456, 1))
    assert_expects(result[0], 123)
    assert_expects(result[1], 456)
    if greenlet:
        result = [None, None]
        coro_test(run, (789, 0), (123, 1))
        assert_expects(result[0], 789)
        assert_expects(result[1], 123)
