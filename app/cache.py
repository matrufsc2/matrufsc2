import hashlib
from bintrees import AVLTree

try:
    import cPickle as pickle
except:
    import pickle
import logging as _logging
import zlib
import time
import gc
import cloudstorage as gcs
from google.appengine.ext import ndb
from google.appengine.api import app_identity

__author__ = 'fernando'

CACHE_TIMEOUT = 86400*7

TEXTCHARS = ''.join(map(chr, [7,8,9,10,12,13,27] + range(0x20, 0x100)))

logging = _logging.getLogger("matrufsc2_cache")
logging.setLevel(_logging.WARNING)
gcs.set_default_retry_params(
    gcs.RetryParams(
        initial_delay=0.2,
        max_delay=5.0,
        min_retries=10,
        max_retries=60,
        backoff_factor=2,
        max_retry_period=30,
        urlfetch_timeout=60
    )
)


class CacheItem(object):
    __slots__ = ["value", "expire_on"]


class LRUItem(object):
    __slots__ = ["value", "key", "updated_on", "accessed_on"]

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)


class LRUCache(AVLTree):
    __slots__ = ["capacity", "expiration", "run_gc", "last_run_gc", "_root", "_count"]

    def __init__(self, *args, **kwargs):
        super(LRUCache, self).__init__(*args, **kwargs)
        self.capacity = 1000
        self.expiration = 86400
        self.run_gc = 0
        self.last_run_gc = 0

    def set_capacity(self, capacity):
        self.capacity = capacity

    def get_capacity(self):
        return self.capacity

    def set_expiration(self, expiration):
        self.expiration = expiration

    def get_expiration(self):
        return self.expiration

    def __getitem__(self, item):
        val = super(LRUCache, self).__getitem__(item)
        val.accessed_on = self.check()
        return val.value

    def get(self, k, d=None):
        try:
            return self[k]
        except KeyError:
            return d

    def pop(self, k, d=None):
        val = self.get(k, d)
        try:
            del self[k]
        except KeyError:
            pass
        return val

    def check(self):
        self.run_gc = (self.run_gc+1)%self.capacity
        now = time.time()
        if self.run_gc == 0 or now > self.last_run_gc:
            self.last_run_gc = now + self.expiration
            # Run and remove expired items first
            expired_items = (item for item in self.values() if now > item.updated_on)
            for expired_item in expired_items:
                del self[expired_item.key]
            dif = len(self)-self.capacity
            while dif > 0 and self:
                expired_item = min(self.values(), key=lambda item: item.accessed_on)
                del self[expired_item.key]
                dif -= 1
                del expired_item
            gc_collect()
        return now

    def __setitem__(self, key, value):
        val = LRUItem()
        val.key = key
        val.value = value
        val.accessed_on = self.check()
        val.updated_on = val.accessed_on + self.expiration
        result = super(LRUCache, self).__setitem__(key, val)
        return result


ndb_context = ndb.get_context()
lru_cache = LRUCache()
lru_cache.set_capacity(100)  # 100 items
lru_cache.set_expiration(3600)  # For 3600 seconds


def gc_collect():
    logging.warning("Collected %d objects with GC",  gc.collect())
    garbage = len(gc.garbage)
    if garbage:
        logging.warning("There are %d objects with reference cycles", garbage)


@ndb.tasklet
def get_gcs_filename(filename):
    bucket_name = lru_cache.get("matrufsc2_bucket_name")
    if not bucket_name:
        bucket_name = ndb_context.memcache_get("matrufsc2_bucket_name").get_result()
        if not bucket_name:
            bucket_name = app_identity.get_default_gcs_bucket_name()
            ndb_context.memcache_set("matrufsc2_bucket_name", bucket_name, CACHE_TIMEOUT).get_result()
        lru_cache["matrufsc2_bucket_name"] = bucket_name
    bucket = "/" + bucket_name
    raise ndb.Return("/".join([bucket, filename]))


@ndb.tasklet
def get_from_cache(key, persistent=True, memcache=True, log=True):
    logging.debug("Fetching key '%s' from cache", key)
    try:
        raise ndb.Return(lru_cache[key])
    except KeyError:
        pass
    start = time.time()
    if memcache:
        result = yield ndb_context.memcache_get(key, use_cache=False)
        if result is not None:
            size = "small"
            if isinstance(result, basestring) and result.translate(None, TEXTCHARS):
                # If result is a string it MAYBE pickled :v
                try:
                    # Try small item first to be more fast :D
                    result = pickle.loads(zlib.decompress(result, 15, 2097152))
                    size = "large"
                except:
                    logging.warn("Error when decompressing content, ignoring..")
                    pass
            if log:
                logging.debug("Found (%s) item on memcache in %f seconds..Returning", size, time.time()-start)
                logging.debug("Saving item on LRU Cache..")
            lru_cache[key] = result
            raise ndb.Return(result)
    if persistent:
        start = time.time()
        filename = yield get_gcs_filename(key)
        try:
            gcs_file = gcs.open(filename, 'r')
            value = gcs_file.read()
            result = pickle.loads(value)
            gcs_file.close()
            if log:
                logging.debug("Found item on GCS in %f seconds..Returning", time.time()-start)
                logging.debug("Saving item on LRU Cache")
            lru_cache[key] = result
            try:
                size = len(value)
                if size >= 1e6:
                    value = zlib.compress(value, 9)
                    if len(value) < 1e6:
                        if log:
                            logging.debug("Saving (large) item on memcached (it has %d bytes)..", size)
                        yield ndb_context.memcache_set(key, value, CACHE_TIMEOUT)
                    else:
                        logging.warn("Ignoring large item because it does not fit on memcache :~")
                else:
                    if log:
                        logging.debug("Saving (small) item on memcached (it has %d bytes)..", size)
                    yield ndb_context.memcache_set(key, result, CACHE_TIMEOUT)
            except:
                pass
            raise ndb.Return(result)
        except Exception, e:
            if isinstance(e, ndb.Return):
                raise e
            elif not isinstance(e, gcs.NotFoundError):
                logging.exception("Error detected when getting from GCS")


def set(key, value, ttl=None):
    """
    Save the item in a non persistent way, compatible to Memcached API.
    :param key: The key that will be saved
    :param value: The value that will be saved
    :param ttl: The TTL of the item that will be solved
    :return:
    """
    item = CacheItem()
    item.value = value
    if ttl is None:
        item.expire_on = None
    else:
        item.expire_on = time.time()+ttl
    key = "memcache-friendly-%s"%hashlib.sha1(key).hexdigest()
    return set_into_cache(key, item, persistent=False).get_result()


def get(key):
    key = "memcache-friendly-%s"%hashlib.sha1(key).hexdigest()
    value = get_from_cache(key).get_result()
    if not value:
        return value
    if isinstance(value, CacheItem):
        if value.expire_on is not None and value.expire_on < time.time():
            value = None
        else:
            value = value.value
    return value


@ndb.tasklet
def set_into_cache(key, value, persistent=True, memcache=True, log=True):
    lru_cache[key] = value
    pickled_value = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
    size = len(pickled_value)
    if log:
        logging.debug("The content saved to cache in the key '%s' has %d bytes", key, size)
    if memcache:
        try:
            if size >= 1e6:
                compressed_value = zlib.compress(pickled_value, 9)
                if len(compressed_value) < 1e6:
                    if log:
                        logging.debug("Saving (large) item on memcached (it has %d bytes)..", size)
                    yield ndb_context.memcache_set(key, compressed_value, CACHE_TIMEOUT)
                else:
                    logging.warn("Ignoring large item because it does not fit on memcache :~")
            else:
                if log:
                    logging.debug("Saving (small) item on memcached")
                yield ndb_context.memcache_set(key, value, CACHE_TIMEOUT)
        except:
            pass
    if persistent:
        try:
            if log:
                logging.debug("Saving item on GCS..")
            filename = yield get_gcs_filename(key)
            gcs_file = gcs.open(filename, 'w')
            gcs_file.write(pickled_value)
            gcs_file.close()
            if log:
                logging.debug("Saved item on GCS..")
        except:
            logging.exception("There is an error when saving to GCS, but okay :v")
            pass


@ndb.tasklet
def delete_from_cache(key, persistent=True):
    logging.debug("Deleting key '%s' from cache", key)
    lru_cache.pop(key, None)
    yield ndb_context.memcache_delete(key, CACHE_TIMEOUT)
    if persistent:
        try:
            filename = yield get_gcs_filename(key)
            gcs.delete(filename)
        except:
            logging.exception("There is an error when deleting from GCS, but okay :v")
            pass


def clear_lru_cache():
    logging.warning("Clearing %d items of the LRU Cache", len(lru_cache))
    lru_cache.clear()
    gc_collect()