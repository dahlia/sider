import collections
from sider import utils


def test_chunk():
    data_length = 1000
    chunk_length = 7
    data = list(range(data_length))
    chunks = utils.chunk(data, chunk_length)
    assert isinstance(chunks, collections.Iterable)
    chunks = list(chunks)
    for i, chunk in enumerate(chunks[:-1]):
        assert len(chunk) == 7
        assert chunk == data[i * chunk_length:(i + 1) * chunk_length]
    assert len(chunks[-1]) == data_length % chunk_length
    assert chunks[-1] == data[(i + 1) * chunk_length:]


def test_chunk_short_data():
    chunks = utils.chunk('asdf', 5)
    chunks = list(chunks)
    assert len(chunks) == 1
    assert chunks[0] == list('asdf')


def test_empty_chunk():
    chunks = utils.chunk([], 10)
    assert len(list(chunks)) == 0
