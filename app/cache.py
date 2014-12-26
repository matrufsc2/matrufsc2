try:
    import cPickle as pickle
except:
    import pickle
import logging
import zlib
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

def get_gcs_filename(filename):
    bucket_name = memcache.get("matrufsc2_bucket_name")
    if not bucket_name:
        bucket_name = app_identity.get_default_gcs_bucket_name()
        memcache.set("matrufsc2_bucket_name", bucket_name)
    bucket = "/" + bucket_name
    return "/".join([bucket, filename])


def get_from_cache(key, persistent=True):
    result = memcache.get(key)
    if result is not None:
        logging.debug("Found item on memcached..Returning")
        try:
            result = pickle.loads(zlib.decompress(result))
        except:
            pass
        return result
    if persistent:
        filename = get_gcs_filename(key)
        try:
            gcs_file = gcs.open(filename, 'r')
            content = gcs_file.read()
            try:
                result = pickle.loads(zlib.decompress(content))
            except:
                result = pickle.loads(content)
            gcs_file.close()
            logging.debug("Found item on GCS..Returning")
            compressed_response = zlib.compress(pickle.dumps(result))
            try:
                logging.debug("Saving item on memcached..")
                memcache.set(key, compressed_response, CACHE_TIMEOUT)
            except:
                pass
            return result
        except:
            pass
    return None


def set_into_cache(key, value, persistent=True):
    compressed_response = zlib.compress(pickle.dumps(value))
    try:
        logging.debug("Saving item on memcached..")
        memcache.set(key, compressed_response, CACHE_TIMEOUT)
    except:
        pass
    if persistent:
        try:
            filename = get_gcs_filename(key)
            gcs_file = gcs.open(filename, 'w')
            gcs_file.write(compressed_response)
            logging.debug("Saving item on GCS..")
            gcs_file.close()
        except:
            pass