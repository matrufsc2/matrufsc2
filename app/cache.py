try:
    import cPickle as pickle
except:
    import pickle
import logging
import zlib
import time
import cloudstorage as gcs
from google.appengine.api import memcache, app_identity

__author__ = 'fernando'

CACHE_TIMEOUT = 600

gcs.set_default_retry_params(
    gcs.RetryParams(
        initial_delay=0.2,
        max_delay=2.0,
        backoff_factor=2,
        max_retry_period=15,
        urlfetch_timeout=10
    )
)

logging = logging.getLogger("matrufsc2_cache")

def get_gcs_filename(filename):
    bucket_name = memcache.get("matrufsc2_bucket_name")
    if not bucket_name:
        bucket_name = app_identity.get_default_gcs_bucket_name()
        memcache.set("matrufsc2_bucket_name", bucket_name, CACHE_TIMEOUT)
    bucket = "/" + bucket_name
    return "/".join([bucket, filename])


def get_from_cache(key, persistent=True):
    start = time.time()
    result = memcache.get(key)
    if result is not None:
        size = "small"
        if isinstance(result, basestring):
            # If result is a string it MAYBE pickled :v
            try:
                # Try small item first to be more fast :D
                size = "large"
                result = pickle.loads(zlib.decompress(result, 15, 2097152))
            except:
                pass
        logging.debug("Found (%s) item on memcache in %f seconds..Returning", size, time.time()-start)
        return result
    if persistent:
        start = time.time()
        filename = get_gcs_filename(key)
        try:
            gcs_file = gcs.open(filename, 'r')
            value = gcs_file.read()
            result = pickle.loads(value)
            gcs_file.close()
            logging.debug("Found item on GCS in %f seconds..Returning", time.time()-start)
            try:
                if len(value) >= 1e6:
                    logging.debug("Saving (large) item on memcached..")
                    memcache.set(key, zlib.compress(value), CACHE_TIMEOUT)
                else:
                    logging.debug("Saving (small) item on memcached..")
                    memcache.set(key, result, CACHE_TIMEOUT)
            except:
                pass
            return result
        except:
            pass
    return None


def set_into_cache(key, value, persistent=True):
    pickled_value = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
    try:
        if len(pickled_value) >= 1e6:
            logging.debug("Saving (large) item on memcached..")
            memcache.set(key, zlib.compress(pickled_value, 1), CACHE_TIMEOUT)
        else:
            logging.debug("Saving (small) item on memcached..")
            memcache.set(key, value, CACHE_TIMEOUT)
    except:
        pass
    if persistent:
        try:
            filename = get_gcs_filename(key)
            gcs_file = gcs.open(filename, 'w')
            gcs_file.write(pickled_value)
            logging.debug("Saving item on GCS..")
            gcs_file.close()
        except:
            logging.debug("There is an error when saving to GCS, but okay :v")
            pass