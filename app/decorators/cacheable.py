from app.cache import get_from_cache, set_into_cache, delete_from_cache
import logging as _logging
import hashlib, json

logging = _logging.getLogger("matrufsc2_decorators_cacheable")
logging.setLevel(_logging.DEBUG)

__author__ = 'fernando'

CACHE_CACHEABLE_KEY = "cache/functions/%s/%s"

def cacheable(consider_only=None):
    def decorator(fn):
        def dec(filters, **kwargs):
            if consider_only is not None and filters:
                filters = {k: filters[k] for k in filters.iterkeys() if k in consider_only}
            filters_hash = hashlib.sha1(json.dumps(filters, sort_keys=True)).hexdigest()
            cache_key = CACHE_CACHEABLE_KEY % (
                fn.__name__,
                filters_hash
            )
            persistent = kwargs.get("persistent", True)
            if kwargs.get("overwrite"):
                update_with = kwargs.get("update_with")
                if update_with:
                    result = get_from_cache(cache_key, persistent=persistent).get_result()
                    if not result:
                        result = update_with
                    if type(result) == type(update_with):
                        logging.debug("Updating cache with passed in value")
                        set_into_cache(cache_key, update_with, persistent=persistent).get_result()
                    else:
                        raise Exception("Types differents: %s != %s" % (str(type(result)), str(type(update_with))))
                elif kwargs.get("exclude"):
                    return delete_from_cache(cache_key, persistent=persistent).get_result()
                else:
                    result = None
            else:
                result = get_from_cache(cache_key, persistent=persistent).get_result()
            if not result:
                result = fn(filters)
                set_into_cache(cache_key, result, persistent=persistent).get_result()
            return result

        dec.__name__ = fn.__name__
        dec.__doc__ = fn.__doc__
        return dec
    return decorator