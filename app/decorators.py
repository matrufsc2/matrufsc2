from app.cache import get_from_cache, set_into_cache
import hashlib
import logging

__author__ = 'fernando'

logging = logging.getLogger("matrufsc2_decorators")
CACHE_SEARCHABLE_KEY = "cache/search/%s/%s"
CACHE_CACHEABLE_KEY = "cache/functions/%s/%s"
CACHE_PAGEABLE_KEY = "cache/page/%s/%s/%d/%d"


def pageable(fn):
    def dec(filters):
        page = int(filters.pop("page", ["1"])[0])
        limit = int(filters.pop("limit", [5])[0])
        result = fn(filters)
        page_start = (page-1)*limit
        page_end = page*limit
        has_more = len(result[page_end:]) > 0
        result = {
            "results": result[page_start:page_end],
            "more": has_more
        }
        return result
    dec.__name__ = fn.__name__
    dec.__doc__ = fn.__doc__
    return dec


def cacheable(consider_only=None):
    def decorator(fn):
        def dec(filters):
            if consider_only is not None:
                new_filters = {}
                for f in consider_only:
                    if filters.has_key(f):
                        new_filters[f] = filters[f]
                logging.debug("After removing all the fields that we do not want, "
                              "we have a size of %d keys (old %d keys)" % (len(new_filters), len(filters)))
                filters = new_filters
            cache_key = CACHE_CACHEABLE_KEY % (fn.__name__, hashlib.sha1(str(filters)).hexdigest())
            result = get_from_cache(cache_key, persistent=True)
            if not result:
                result = fn(filters)
                set_into_cache(cache_key, result, persistent=True)
            return result
        dec.__name__ = fn.__name__
        dec.__doc__ = fn.__doc__
        return dec
    return decorator


def searchable(fn):
    def dec(filters):
        query = filters.pop("q", None)
        if query:
            query = str(query[0]).lower()
            cache_key = CACHE_SEARCHABLE_KEY % (
                hashlib.sha1(str(filters)).hexdigest(),
                hashlib.sha1(query).hexdigest()
            )
            result = get_from_cache(cache_key, False)
            if result is None:
                logging.debug("No result found. Getting lists of disciplines that match the filters without the queries")
                result = fn(filters)
                logging.debug("Searching for results that match '%s'", query)
                result = filter(lambda item: query in item.get_formatted_string().lower(), result)
                logging.debug("Saving cache search for '%s'", query)
                set_into_cache(cache_key, result, False)
        else:
            result = fn(filters)
        return result
    dec.__name__ = fn.__name__
    dec.__doc__ = fn.__doc__
    return dec