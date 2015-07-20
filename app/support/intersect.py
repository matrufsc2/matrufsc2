__author__ = 'fernando'


def intersect(x, y):
    x = iter(x if x else []).next
    y = iter(y if y else []).next
    xo = x()
    yo = y()
    while 1:
        if xo == yo:
            yield xo
            xo = x()
            yo = y()
        elif xo > yo:
            yo = y()
        else:
            xo = x()