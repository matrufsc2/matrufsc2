import json
import time
from google.appengine.ext import ndb
from app.cache import get_from_cache, set_into_cache, clear_lru_cache, gc_collect
from app.json_serializer import JSONEncoder
from app.support.islice import islice
from app.support.intersect import intersect
from app.support.sift3 import sift3
from app.support.Trie import Trie
from collections import defaultdict
import logging as _logging
import hashlib, itertools, pprint
from unidecode import unidecode

__author__ = 'fernando'

logging = _logging.getLogger("matrufsc2_searchable")
logging.setLevel(_logging.DEBUG)

CACHE_INDEX_KEY = "cache/searchIndex/%s/%s/%s"

def searchable(get_formatted_string, prefix=None, consider_only=None, min_word_length=1):
    if consider_only is None:
        consider_only = []
    consider_only.extend(["page", "limit", "q"])
    if prefix is None:
        prefix = ""

    def decorator(fn):
        def dec(filters, **kwargs):
            start_processing = time.time()
            filters = {k: filters[k] for k in filters.iterkeys() if k in consider_only}
            original_query = filters.pop("q", "")
            query = unidecode(unicode(original_query)).lower()
            page = int(filters.pop("page", 1))
            limit = int(filters.pop("limit", 5))
            page_start = (page - 1) * limit
            page_end = page * limit
            filters_hash = hashlib.sha1(json.dumps(filters, sort_keys=True)).hexdigest()
            items_key = CACHE_INDEX_KEY % (
                fn.__name__,
                filters_hash,
                "items"
            )
            query_words = filter(None, map(lambda word: "".join(filter(str.isalnum, word)), query.split()))
            if query_words:
                logging.debug("Doing search based on query '%s'..", query)
                index_key = CACHE_INDEX_KEY % (
                    fn.__name__,
                    filters_hash,
                    "index"
                )
                words_key = CACHE_INDEX_KEY % (
                    fn.__name__,
                    filters_hash,
                    "words"
                )
                if kwargs.get("overwrite"):
                    index, items = None, None
                    update_with = kwargs.get("update_with")
                    if update_with:
                        logging.debug("Detected instruction to update items list..okay")
                        old_items = get_from_cache(items_key, persistent=True).get_result()
                        items = []
                        update_with = json.loads(json.dumps(update_with, cls=JSONEncoder, separators=(',', ':')))
                        updated_items = []
                        old_items_ids = []
                        for item in old_items:
                            item["id"] = item["id"].replace(prefix, "")
                            if item["id"] in old_items_ids:
                                continue
                            old_items_ids.append(item["id"])
                            for new_item in update_with:
                                new_item["id"] = new_item["id"].replace(prefix, "")
                                if str(item["id"]) == str(new_item["id"]):
                                    logging.warn("Detected update to the item '%s' == '%s'", item["id"], new_item["id"])
                                    items.append(new_item)
                                    updated_items.append(new_item["id"])
                                    break
                            else:
                                items.append(item)
                        logging.debug("Updated %d items", len(updated_items))
                        inserted_count = 0
                        for new_item in update_with:
                            if new_item["id"] in updated_items:
                                continue
                            logging.debug("Adding item '%s' to the items list", new_item["id"])
                            items.append(new_item)
                            inserted_count += 1
                        logging.debug("Inserted %d items", inserted_count)
                        if inserted_count + len(updated_items) != len(update_with):
                            logging.warning("There is %d items duplicated",
                                            len(filter(lambda item: updated_items.count(item) > 1, updated_items)))
                            logging.warning(
                                "Expected to update/insert %d items but inserted %d items and updated %d items" % (
                                    len(update_with), inserted_count, len(updated_items)))
                else:
                    index_items = [
                        get_from_cache(index_key, persistent=True),
                        get_from_cache(items_key, persistent=True)
                    ]
                    index = index_items[0].get_result()
                    if min_word_length == 1 and index and isinstance(index, Trie) and hasattr(index, "nodes"):
                        logging.warning("Resetting index status because of invalid format "
                                        "(it should be a Trie, but it is %s)"%type(index).__name__)
                        index = None
                    elif min_word_length > 1 and index and not isinstance(index, dict):
                        logging.warning("Resetting index status because of invalid format "
                                        "(it should be a dict, but it is %s)"%type(index).__name__)
                        index = None
                    items = index_items[1].get_result()
                if kwargs.get("index"):
                    logging.debug("Index not found, creating index..(as authorized)")
                    if min_word_length == 1:
                        logging.debug("Creating a Trie instance")
                        index = Trie()
                        index.editable = True
                    else:
                        logging.debug("Creating a default dict instance")
                        index = defaultdict(lambda: [])
                    items_ids = {}
                    start = time.time()
                    index_words = []

                    if items is None:
                        clear_lru_cache()  # We need nothing before calling the original function..
                        items = fn(filters)
                        clear_lru_cache()  # To guarantee that the memory is clean
                    else:
                        logging.warn("Detected update with %d items", len(items))
                    logging.debug("Simplifying %d items..", len(items))
                    clear_lru_cache()
                    items = json.loads(JSONEncoder(separators=(',', ':')).encode(items))
                    clear_lru_cache()
                    logging.debug("%d Items simplified in %f seconds!", len(items), time.time() - start)
                    logging.debug("Filtering non None items on the list of results (total actually: %d)", len(items))
                    items = filter(lambda item: item and isinstance(item, dict), items)
                    logging.debug("Filtering non None items on the list of results. Now we have %d items", len(items))
                    exclude = kwargs.get("exclude", [])
                    if exclude:
                        logging.debug("Excluding %d specified items..", len(exclude))
                        if prefix:
                            exclude = map(lambda exclude_item: exclude_item.replace(prefix, ""), exclude)
                        items = filter(lambda item: item["id"] not in exclude, items)
                    logging.debug("Creating list of words based on %d items..", len(items))
                    for item_id, item in enumerate(items):
                        if item["id"].startswith(prefix):
                            item["id"] = item["id"][len(prefix):]
                        if item["id"] in items_ids:
                            logging.debug("The task already exists! Ignoring..")
                            continue
                        words = get_formatted_string(item).lower().split()
                        index_words.extend(
                            map(
                                lambda word: [word, len(word), item],
                                filter(
                                    lambda word: len(word) >= min_word_length,
                                    map(
                                        lambda word: "".join(filter(unicode.isalnum, word)),
                                        words
                                    )
                                )
                            )
                        )
                        index_words.extend(
                            map(
                                lambda word: [word, len(word), item],
                                filter(
                                    lambda word: len(word) >= min_word_length,
                                    map(
                                        lambda word: "".join(filter(unicode.isdigit, word)),
                                        words
                                    )
                                )
                            )
                        )
                        items_ids[item["id"]] = item_id
                    logging.debug("List of words created in %f seconds with %d words", time.time() - start,
                                  len(index_words))
                    index_words.sort(key=lambda item: item[0])
                    word = None
                    word_items = []
                    for index_word in index_words:
                        if word is None:
                            word = index_word[0]
                        if word != index_word[0]:
                            index[word].extend(set([items_ids[item['id']] for item in word_items]))
                            index[word].sort()
                            word = index_word[0]
                            word_items = []
                        word_items.append(index_word[2])
                    if word is not None:
                        index[word].extend(set([items_ids[item['id']] for item in word_items]))
                        index[word].sort()
                    del index_words
                    if min_word_length == 1:
                        index.editable = False
                    else:
                        index = dict(index)
                    del items_ids
                    start = time.time()
                    logging.debug(
                        "Saving processed result with %d items in storage and %d items in index..",
                        len(items),
                        len(index)
                    )
                    logging.debug("The index is being saved as a %s", type(index).__name__)
                    futures = [
                        set_into_cache(index_key, index, persistent=True),
                        set_into_cache(items_key, items, persistent=True)
                    ]
                    if min_word_length == 1:
                        futures.append(set_into_cache(words_key, list(index.get_words()), persistent=True))
                    ndb.Future.wait_all(futures)
                    logging.debug("Saving made in %f seconds", time.time() - start)
                elif index is None or items is None:
                    logging.warn("Index not found and not authorized :v")
                    pprint.pprint(filters)
                    index = Trie()
                    items = []
                suggestions = []
                if min_word_length == 1:
                    found = [[i, word, list(index.get_list(word))] for i, word in enumerate(query_words)]
                else:
                    found = [[i, word, list(index.get(word, []))] for i, word in enumerate(query_words)]
                not_found = []
                results = None
                for item in found:
                    if not item[2]:
                        not_found.append([item[0], item[1]])
                        continue
                    if results is None:
                        results = item[2]
                    else:
                        results = intersect(results, item[2])
                results = list(results if results else [])
                if not results and not not_found:
                    # If no results are found, search for a suggestion if possible
                    not_found = [[item[0], item[1]] for item in found]
                queue = []
                if not_found and min_word_length == 1: # If each letter is individually indexed, we can suggest things!
                    all_words = get_from_cache(words_key).get_result()
                    if all_words:
                        words_cache = {}
                        for item in not_found:
                            l = len(item[1])
                            if l not in words_cache:
                                words_cache[l] = [word for word in all_words if len(word) >= l]
                            item_suggestions = islice(sorted(
                                words_cache[l],
                                key=lambda word: sift3(word, item[1])
                            ), 0, 50)
                            queue.extend([item, suggestion, list(index.get_list(suggestion))] for suggestion in item_suggestions)
                        del words_cache
                    if results:
                        get_results = lambda item: list(islice(reduce(intersect, map(lambda suggestion: suggestion[2], item)+[results]), 0, 10))
                    else:
                        get_results = lambda item: list(islice(reduce(intersect, map(lambda suggestion: suggestion[2], item)), 0, 10))
                    not_found_total = len(not_found)
                    for n in xrange(not_found_total, 0, -1):
                        new_queue = (item for item in itertools.combinations(queue, r=n) if len(set(s[0][0] for s in item)) == len(item))
                        for item in new_queue:
                            results_list = get_results(item)
                            if results_list:
                                sug = query_words[:]
                                # Replace the initial suggestions in the original query words
                                for s in item:
                                    sug[s[0][0]] = s[1]
                                if sift3(query, " ".join(sug)) > 10:
                                    continue
                                if n < not_found_total:
                                    # Eliminates words not included in the suggestion in case of trying suggestions
                                    # with less words than wrong words
                                    item_indexes = [s[0][0] for s in item]
                                    for s in sorted(not_found, key=lambda s: s[0], reverse=True):
                                        if s[0] not in item_indexes:
                                            del sug[s[0]]

                                results_list_items = map(items.__getitem__, results_list)

                                # Reorganize the words of the suggestions in the correct order
                                # (ex.: 'organizacao no computadores' -> 'organizacao computadores no')
                                r = get_formatted_string(results_list_items[0]).lower().split(" ")
                                r = map(
                                    lambda word: "".join(filter(unicode.isalnum, word)),
                                    r
                                )
                                nsug = []
                                for i in r:
                                    for s in sug:
                                        if i.startswith(s):
                                            if s not in nsug and len(s) > 2:
                                                nsug.append(s)
                                if nsug:
                                    sug = nsug

                                # Check if the words does not match itself in the suggestion
                                # (ex.: 'estruturas da dados' is ignored here)
                                invalid = False
                                for i, s in enumerate(sug):
                                    for i2, s2 in enumerate(sug):
                                        if i2 == i:
                                            continue
                                        if s.startswith(s2):
                                            invalid = True
                                            break
                                    if invalid:
                                        break
                                if invalid:
                                    continue

                                sug = " ".join(sug)

                                if sug in suggestions:
                                    continue
                                first = False
                                for result_in_list in results_list_items:
                                    if sug in get_formatted_string(result_in_list).lower():
                                        # If the suggestion matches the string in the correct order, stop the processing
                                        if len(results_list_items) == 1:
                                            suggestions = [sug]
                                        else:
                                            suggestions.insert(0, sug)
                                        first = True
                                        break
                                if first:
                                    break
                                else:
                                    suggestions.append(sug)
                                    if len(suggestions) > 5:
                                        break
                        if suggestions:  # If we already have suggestions, stops the loop!
                            break

                # If the total number of results is less than N items, we send all the results we found
                items_len = len(items)
                results = [result for result in results if result < items_len]
                prefetch = next(islice(results, 40, 41), False) is False
                if not prefetch:
                    # if not prefetch, slice the results according to page and limit variables
                    results = islice(results, page_start, page_end)
                results = map(items.__getitem__, results)
                if suggestions:
                    prefetch = False
                    results = []
                    suggestions = sorted(suggestions, key=lambda suggestion: sift3(query, suggestion))
            else:
                if kwargs.get("overwrite"):
                    items = None
                else:
                    items = get_from_cache(items_key, persistent=True).get_result()
                if kwargs.get("index"):
                    items = fn(filters)
                    items = json.loads(json.dumps(items, cls=JSONEncoder, separators=(',', ':')))
                    for item in items:
                        if item["id"].startswith(prefix):
                            item["id"] = item["id"][len(prefix):]
                    set_into_cache(items_key, items, persistent=True).get_result()
                elif items is None:
                    items = []
                results = list(islice(items, page_start, page_end))
                prefetch = False
                suggestions = []
            results = {
                "more": bool(results) and not prefetch,
                "results": results,
                "id_prefix": prefix,
                "prefetch": prefetch,
                "suggestions": suggestions,
                "query": original_query if original_query else None
            }
            start_processing = time.time() - start_processing
            logging.debug(
                "Found %d itens (in a total of %d itens) that matches the search '%s' in %f seconds",
                len(results["results"]),
                len(items),
                query,
                start_processing
            )
            return results

        dec.__name__ = fn.__name__
        dec.__doc__ = fn.__doc__
        return dec

    return decorator