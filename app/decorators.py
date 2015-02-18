import time
from app.cache import get_from_cache, set_into_cache, pickle
import hashlib
import logging
import json
from collections import OrderedDict
from app.json_serializer import JSONEncoder

__author__ = 'fernando'

logging = logging.getLogger("matrufsc2_decorators")
CACHE_SEARCHABLE_KEY = "cache/search/%s/%s/%d/%d"
CACHE_INDEX_KEY = "cache/searchIndex/%s/%s"
CACHE_CACHEABLE_KEY = "cache/functions/%s/%s"


def cacheable(consider_only=None):
    def decorator(fn):
        def dec(filters, **kwargs):
            if consider_only is not None and filters:
                new_filters = {}
                for f in consider_only:
                    if filters.has_key(f):
                        new_filters[f] = filters[f]
                logging.debug("After removing all the fields that we do not want, "
                              "we have a size of %d keys (old %d keys)" % (len(new_filters), len(filters)))
                if new_filters:
                    logging.debug("These keys are: %s", ", ".join(new_filters))
                filters = new_filters
            cache_key = CACHE_CACHEABLE_KEY % (
                fn.__name__,
                hashlib.sha1(json.dumps(filters, sort_keys=True)).hexdigest()
            )
            if kwargs.get("overwrite"):
                result = None
            else:
                result = get_from_cache(cache_key, persistent=True)
            if not result:
                result = fn(filters)
                set_into_cache(cache_key, result, persistent=True)
            return result
        dec.__name__ = fn.__name__
        dec.__doc__ = fn.__doc__
        return dec
    return decorator

def searchable(get_formatted_string, prefix=None, consider_only=None):
    if consider_only:
        consider_only.extend(["q", "page", "limit"])
    def decorator(fn):
        def dec(filters, **kwargs):
            if consider_only and filters:
                new_filters = {}
                for f in consider_only:
                    if filters.has_key(f):
                        new_filters[f] = filters[f]
                logging.debug("After removing all the fields that we do not want, "
                              "we have a size of %d keys (old %d keys)" % (len(new_filters), len(filters)))
                if new_filters:
                    logging.debug("These keys are: %s", ", ".join(new_filters))
                filters = new_filters
            query = filters.pop("q", "")
            page = int(filters.pop("page", 1))
            limit = int(filters.pop("limit", 5))
            page_start = (page-1) * limit
            page_end = page * limit
            query = str(query).lower()
            start_processing = time.time()
            filters_hash = hashlib.sha1(fn.__name__+json.dumps(filters, sort_keys=True)).hexdigest()
            items_key = CACHE_INDEX_KEY % (
                filters_hash,
                "items"
            )

            logging.debug("Doing search based on query '%s'..", query)
            query_words = filter(lambda word: "".join(filter(str.isalnum, word.strip())), query.split())
            if query_words:
                logging.debug("Loading index..")
                start = time.time()
                storage_key = CACHE_INDEX_KEY % (
                    filters_hash,
                    "index"
                )
                if kwargs.get("overwrite"):
                    index = None
                else:
                    index = get_from_cache(storage_key, persistent=True)

                if index:
                    logging.debug("Index loaded in %f seconds", time.time()-start)
                elif kwargs.get("index"):
                    logging.debug("Index not found, creating index..(as authorized)")
                    index = {}
                    items_ids = {}
                    start = time.time()
                    index_words = []

                    logging.debug("Creating list of words..")
                    items = fn(filters)
                    items = json.loads(json.dumps(items, cls=JSONEncoder, separators=(',', ':')))
                    for item_id, item in enumerate(items):
                        if prefix:
                            item["id"] = item["id"].replace(prefix, "")
                        index_words.extend(
                            map(
                                lambda word: [word, len(word), item],
                                filter(
                                    lambda word: len(word) >= 1,
                                    map(
                                        lambda word: "".join(filter(unicode.isalnum, word)),
                                        get_formatted_string(item).lower().split()
                                    )
                                )
                            )
                        )
                        items_ids[item["id"]] = item_id
                    logging.debug("List of words created in %f seconds", time.time()-start)
                    index_words.sort(key=lambda item: item[0])
                    if index_words:
                        max_letter = max(index_words, key=lambda item: len(item[0]))
                    else:
                        max_letter = [None, 0, None]
                    word = None
                    word_items = []
                    for crop_at in xrange(1, len(max_letter[0])+1):
                        for index_word in (index_word for index_word in index_words if index_word[1] >= crop_at):
                            if word is None:
                                word = str(index_word[0][:crop_at])
                            if word != index_word[0][:crop_at]:
                                keys_to_items = OrderedDict(zip([items_ids[item['id']] for item in word_items], word_items))
                                index[word] = keys_to_items.keys()
                                word = str(index_word[0][:crop_at])
                                word_items = []
                            word_items.append(index_word[2])
                        if word is not None:
                            keys_to_items = OrderedDict(zip([items_ids[item['id']] for item in word_items], word_items))
                            index[word] = keys_to_items.keys()
                    start = time.time()
                    logging.debug("Saving mapping from word to itens..")
                    set_into_cache(storage_key, index, persistent=True)
                    logging.debug("Saving items of the index..")
                    set_into_cache(items_key, items, persistent=True)
                    logging.debug("Saving made in %f seconds", time.time()-start)
                else:
                    logging.debug("Index not found and not authorized :v")
                    index = {}
                results = None
                start = time.time()
                for query_word in query_words:
                    found = index.get(query_word, [])
                    logging.debug("Found %d matches for word '%s'. Breaking..", len(found), query_word)
                    if not found:
                        break
                    elif results is None:
                        results = found
                    elif len(results) > len(found):
                        results = filter(found.__contains__, results)
                    else:
                        results = filter(results.__contains__, found)
                    if not results:
                        break
                if results is None:
                    results = []
                results = list(results)
                logging.debug("%f seconds to find %d matches in the index", time.time()-start, len(results))
                has_more = len(results[page_end:]) > 0
                results = results[page_start:page_end]

                if results:
                    logging.debug("Found %d results. Loading items...", len(results))
                    items = get_from_cache(items_key, persistent=True)
                    results = [items[result] for result in results]
                    results = filter(lambda item: query in get_formatted_string(item).lower(), results)
                    if prefix:
                        for result in results:
                            result["id"] = "".join([prefix,result["id"]])
                logging.debug(
                    "Found %d itens that matches the search in %f seconds",
                    len(results),
                    time.time()-start_processing
                )
            else:
                if kwargs.get("overwrite"):
                    results = None
                else:
                    results = get_from_cache(items_key, persistent=True)
                if kwargs.get("index"):
                    results = fn(filters)
                    results = json.loads(json.dumps(results, cls=JSONEncoder, separators=(',', ':')))
                    if prefix:
                        for result in results:
                            result["id"] = result["id"].replace(prefix, "")
                    set_into_cache(items_key, results, persistent=True)
                elif results is None:
                    results = []
                has_more = len(results[page_end:]) > 0
                results = results[page_start:page_end]
                if prefix:
                    for result in results:
                        result["id"] = "".join([prefix, result["id"]])
                logging.debug("Loading of entities done in %f seconds", time.time()-start_processing)
            results = {
                "more": has_more,
                "results": results
            }
            return results
        dec.__name__ = fn.__name__
        dec.__doc__ = fn.__doc__
        return dec
    return decorator