__author__ = 'fernando'


def islice(iterable, start, end=None):
    iterable = iter(iterable if iterable else [])
    if end is not None:
        end = start - end + 1
        for item in iterable:
            start -= 1
            if start >= 0:
                continue
            yield item
            if start < end:
                break
    else:
        for item in iterable:
            start -= 1
            if start >= 0:
                continue
            yield item