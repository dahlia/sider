import os


exttest_count = 0


def test_ext():
    from sider.ext import _exttest
    assert _exttest.ext_loaded == 'yes'
    assert exttest_count == 1
    from sider import ext
    assert ext._exttest is _exttest
    try:
        import sider.ext._noexttest
    except ImportError as e:
        assert str(e) == "No module named 'sider.ext._noexttest'"
    else:
        assert False, 'it must raise ImportError'


def test_print_version():
    from sider.version import VERSION
    printed_version = os.popen('python -m sider.version').read().strip()
    assert printed_version == VERSION
