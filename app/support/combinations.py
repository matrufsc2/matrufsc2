from app.support.ijoin import ijoin

__author__ = 'fernando'


def combinations(items, limit=None):
    items = [list(item) for item in items]
    items_size = len(items)
    if limit is None or items_size == limit:
        result = None
        for item in items:
            if result is None:
                result = [[x] for x in item]
            else:
                result = [y+[x] for y in result for x in item]
        if not result:
            result = []
        return iter(result)
    elif items_size > limit:
        result = []
        to_try = combinations([range(items_size) for _ in xrange(limit)])
        for combination in to_try:
            if len(set(combination)) != len(combination) or sorted(combination) != combination:
                continue
            result.append(combinations([items[index] for index in combination]))
        return ijoin(result)
    else:
        return iter([])
