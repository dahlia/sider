import threading
from attest import Tests, assert_hook, raises
from sider.threadlocal import get_ident


tests = Tests()


@tests.test
def ident():
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

