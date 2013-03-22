import itertools


def chunk(iterable, n):
    """Splits an iterable into a list of length ``n``.

    If the iterable is finite, The last element may be shorter than
    the other chunks, depending on the length of the iterable.

    """
    i = iter(iterable)
    return iter(lambda: list(itertools.islice(i, n)), [])
