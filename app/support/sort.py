__author__ = 'fernando'


def sort(x, y):
    x = iter(x if x else []).next
    y = iter(y if y else []).next
    try:
        xo = x()
    except StopIteration:
        while 1:
            yield y()
        raise StopIteration
    try:
        yo = y()
    except StopIteration:
        yield xo
        while 1:
            yield x()
    while 1:
        if xo == yo:
            yield xo
            try:
                xo = x()
            except StopIteration:

                if xo != yo:
                    yield yo
                while 1:
                    yield y()
            try:
                yo = y()
            except StopIteration:
                yield xo
                while 1:
                    yield x()
        elif xo > yo:
            yield yo
            try:
                yo = y()
            except StopIteration:
                if xo != yo:
                    yield xo
                while 1:
                    yield x()
        else:
            yield xo
            try:
                xo = x()
            except StopIteration:
                if xo != yo:
                    yield yo
                while 1:
                    yield y()