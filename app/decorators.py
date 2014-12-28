import time
from app.cache import get_from_cache, set_into_cache
import hashlib
import logging
from collections import OrderedDict
__author__ = 'fernando'

logging = logging.getLogger("matrufsc2_decorators")
CACHE_SEARCHABLE_KEY = "cache/search/%s/%s/%d/%d"
CACHE_INDEX_KEY = "cache/searchIndex/%s/%d/%s"
CACHE_CACHEABLE_KEY = "cache/functions/%s/%s"


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
                logging.debug("These keys are: %s", ", ".join(new_filters))
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
        query = filters.pop("q", [""])
        page = int(filters.pop("page", [1])[0])
        limit = int(filters.pop("limit", [5])[0])
        query = str(query[0]).lower()
        start_processing = time.time()

        logging.debug("Doing search based on query '%s'..", query)
        query_words = filter(lambda word: word.strip(), query.split())
        if query_words:
            max_word = max(query_words, key=lambda word: len(word))
            max_word = "".join(filter(str.isalnum, max_word))
            max_word_size = len(max_word)
            first_letters = max_word[:3]

            if max_word_size > 30:
                max_word_size = max_word[:30]
                max_word_size = 30


            logging.debug("Loading index..")
            start = time.time()
            storage_key = CACHE_INDEX_KEY % (
                hashlib.sha1(str(filters)).hexdigest(),
                max_word_size,
                first_letters
            )
            index = get_from_cache(storage_key, persistent=True)
            logging.debug("Index loaded in %f seconds", time.time()-start)
            if not index:
                logging.debug("Index not found, creating index..")
                index = {
                    "keys": {},
                    "words": {}
                }
                start = time.time()
                index_words = []


                logging.debug("Creating list of words..")
                for item in fn(filters):
                    index_words.extend(
                        map(
                            lambda word: [word[:max_word_size], item],
                            filter(
                                lambda word: first_letters == word[:3] and len(word) >= max_word_size,
                                map(
                                    lambda word: "".join(filter(unicode.isalnum, word)),
                                    item.get_formatted_string().lower().split()
                                )
                            )
                        )
                    )
                logging.debug("List of words created in %f seconds", time.time()-start)
                index_words.sort(key=lambda item: item[0])
                # max_letter = max(index_words, key=lambda item: item[1])
                # logging.debug("Larger word found has %d letters: %s", max_letter[1], max_letter[0])
                word = None
                word_items = []
                # for crop_at in xrange(0, max_letter[1]+1):
                start_letter = time.time()
                for index_word in index_words:
                    if word is None:
                        word = index_word[0]
                    if word != index_word[0]:
                        keys_to_items = OrderedDict(zip([item.key.id() for item in word_items], word_items))
                        index["keys"].update(keys_to_items)
                        index["words"][word] = keys_to_items.keys()
                        word = index_word[0]
                        word_items = []
                    word_items.append(index_word[1])
                if word is not None:
                    keys_to_items = OrderedDict(zip([item.key.id() for item in word_items], word_items))
                    index["keys"].update(keys_to_items)
                    index["words"][word] = keys_to_items.keys()
                logging.debug(
                    "%f seconds to process %d words with %d letters (and %d itens)",
                    time.time()-start_letter,
                    len(index["words"]),
                    max_word_size,
                    len(index["keys"])
                )
                start = time.time()
                logging.debug("Saving index..")
                set_into_cache(storage_key, index, persistent=True)
                logging.debug("Saving made in %f seconds", time.time()-start)
            results = index["words"].get(max_word, [])
            results = map(lambda key: index["keys"][key], results)
            results = filter(lambda item: query in item.get_formatted_string().lower(), results)
        else:
            results = fn(filters)

        page_start = (page-1) * limit
        page_end = page * limit
        has_more = len(results[page_end:]) > 0
        documents = results[page_start:page_end]
        result = {
            "more": has_more,
            "results": documents
        }
        return result
    dec.__name__ = fn.__name__
    dec.__doc__ = fn.__doc__
    return dec