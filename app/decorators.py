from collections import defaultdict
import pprint
import time
import itertools
from unidecode import unidecode
from app.cache import get_from_cache, set_into_cache, delete_from_cache, LRUCache
from google.appengine.ext import ndb
import threading
import Queue
import hashlib
import logging as _logging
import json
from bintrees import AVLTree
from app.json_serializer import JSONEncoder

__author__ = 'fernando'

logging = _logging.getLogger("matrufsc2_decorators")
logging.setLevel(_logging.DEBUG)
CACHE_INDEX_KEY = "cache/searchIndex/%s/%s/%s"
CACHE_CACHEABLE_KEY = "cache/functions/%s/%s"
filters_cache = LRUCache()
filters_cache.set_expiration(86400 * 365)


def cacheable(consider_only=None):
    def decorator(fn):
        def dec(filters, **kwargs):
            if consider_only is not None and filters:
                filters = {k: filters[k] for k in filters.iterkeys() if k in consider_only}
            try:
                filters_hash = filters_cache[filters]
            except KeyError:
                filters_hash = hashlib.sha1(json.dumps(filters, sort_keys=True)).hexdigest()
                filters_cache[filters] = filters_hash
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


def sort(x, y):
    x = iter(x if x else []).next
    y = iter(y if y else []).next
    try:
        xo = x()
    except StopIteration:
        while 1:
            yield y()
        raise StopIteration
    try:
        yo = y()
    except StopIteration:
        yield xo
        while 1:
            yield x()
    while 1:
        if xo == yo:
            yield xo
            try:
                xo = x()
            except StopIteration:
                yield yo
                while 1:
                    yield y()
            try:
                yo = y()
            except StopIteration:
                yield xo
                while 1:
                    yield x()
        elif xo > yo:
            yield yo
            try:
                yo = y()
            except StopIteration:
                yield xo
                while 1:
                    yield x()
        else:
            yield xo
            try:
                xo = x()
            except StopIteration:
                yield yo
                while 1:
                    yield y()


class Trie(AVLTree):
    def __init__(self):
        super(Trie, self).__init__()
        self.nodes = []
        self.__editable__ = True
        self.__step__ = 1

    def __getstate__(self):
        s = super(Trie, self).__getstate__()
        if self.nodes:
            s["nodes"] = self.nodes
        if self.__editable__ is True:
            s["editable"] = self.__editable__
        if self.__step__ != 1:
            s["step"] = self.__step__
        return s

    def __setstate__(self, state):
        self.nodes = state.pop("nodes", [])
        self.__editable__ = state.pop("editable", False)
        self.__step__ = state.pop("step", 1)
        super(Trie, self).__setstate__(state)

    def append(self, val):
        return self.nodes.append(val)

    def sort(self):
        return self.nodes.sort()

    def extend(self, values):
        return self.nodes.extend(values)

    def remove(self, val):
        return self.items_ids.remove(val)

    @property
    def editable(self):
        return self.__editable__

    @editable.setter
    def editable(self, editable):
        queue = [self]
        while queue:
            el = queue.pop()
            el.__editable__ = editable
            queue.extend(el.values())

    @property
    def step(self):
        return self.__step__

    @step.setter
    def step(self, step):
        queue = [self]
        while queue:
            el = queue.pop()
            el.__step__ = step
            queue.extend(el.values())

    @classmethod
    def from_keys(cls, iterable):
        tree = cls()
        for k in iterable:
            tree[k]
        return tree

    def as_list(self):
        queue = [self]
        i = 0
        while i < len(queue):
            el = queue[i]
            queue.extend(el.values())
            i += 1
        queue = [item.nodes for item in queue]
        while len(queue) > 1:
            item_old = None
            temp = []
            for item in queue:
                if item_old is None:
                    item_old = item
                else:
                    temp.append(sort(item, item_old))
                    item_old = None
            if item_old is not None:
                temp[-1] = sort(item_old, temp[-1])
            queue = temp
        if queue:
            return queue[0]
        return []

    def has_key(self, item):
        if len(item) > self.__step__:
            s = self
            try:
                buf = list(item)
                while buf:
                    letter = "".join(islice(buf, 0, s.__step__))
                    buf = list(islice(buf, s.__step__))
                    s = s[letter]
            except KeyError:
                return False
            return True
        return item in self.keys()

    def __getitem__(self, item):
        if len(item) > self.__step__:
            s = self
            try:
                buf = list(item)
                while buf:
                    letter = "".join(islice(buf, 0, s.__step__))
                    buf = list(islice(buf, s.__step__))
                    s = s[letter]
            except KeyError:
                raise KeyError(item)
            return s
        try:
            value = super(Trie, self).__getitem__(item)
        except KeyError:
            if self.__editable__:
                self[item] = value = Trie()
                value.__step__ = self.__step__
            elif len(self) == 0: #If its not editable its ok to simply return the actual instance
                return self
            else:
                value = Trie()
                value.__editable__ = False
        return value

    def __setitem__(self, key, value):
        if isinstance(value, Trie):
            return super(Trie, self).__setitem__(key, value)
        raise NotImplementedError

    def __delitem__(self, key):
        if len(key) > 1:
            s = self
            for letter in key[:-1]:
                s = s[letter]
            del s[-1]
        return super(Trie, self).__delitem__(key)

    def get(self, key, default):
        editable = self.__editable__
        if editable is True:
            self.set_editable(False)
        try:
            val = self[key]
            if editable is True:
                self.set_editable(editable)
            return val
        except KeyError:
            if editable is True:
                self.set_editable(editable)
            return default

    def get_words(self):
        edit = self.editable
        if edit is True:
            self.editable = False
        s = self
        try:
            queue = [[k, val] for k, val in s.items()]
            while queue:
                sug = queue.pop()
                queue.extend([["".join([sug[0],k]), val] for k, val in sug[1].items()])
                if sug[1].nodes:
                    yield sug[0]
        finally:
            if edit is True:
                self.editable = edit


def islice(iterable, start, end=None):
    iterable = iter(iterable if iterable else [])
    if end is not None:
        end = start - end + 1
        for item in iterable:
            start -= 1
            if start >= 0:
                continue
            yield item
            if start < end:
                break
    else:
        for item in iterable:
            start -= 1
            if start >= 0:
                continue
            yield item

sift3_offset = xrange(1, 3)

def sift3(s1, s2):
    s1L = len(s1)
    s2L = len(s2)
    c1 = 0
    c2 = 0
    lcs = 0
    while c1 < s1L and c2 < s2L:
        if s1[c1] == s2[c2]:
            lcs += 1
        else:
            for i in sift3_offset:
                if c1 + i < s1L and s1[c1 + i] == s2[c2]:
                    c1 += i
                    break
                if c2 + i < s2L and s1[c1] == s2[c2 + i]:
                    c2 += i
                    break
        c1 += 1
        c2 += 1
    return (s1L+s2L)/2 - lcs


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
            try:
                filters_hash = filters_cache[filters]
            except KeyError:
                filters_hash = hashlib.sha1(json.dumps(filters, sort_keys=True)).hexdigest()
                filters_cache[filters] = filters_hash
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
                            print map(lambda item: item["id"], update_with)
                            print updated_items
                            logging.warning("There is %d items duplicated",
                                            filter(lambda item: updated_items.count(item) > 1, updated_items))
                            logging.warning(
                                "Expected to update/insert %d items but inserted %d items and updated %d items" % (
                                    len(update_with), inserted_count, len(updated_items)))
                else:
                    index_items = [
                        get_from_cache(index_key, persistent=True),
                        get_from_cache(items_key, persistent=True)
                    ]
                    ndb.Future.wait_all(index_items)
                    index = index_items[0].get_result()
                    items = index_items[1].get_result()
                    if not isinstance(index, Trie):
                        index = None
                if kwargs.get("index"):
                    logging.debug("Index not found, creating index..(as authorized)")
                    index = Trie()
                    index.step = min_word_length
                    items_ids = AVLTree()
                    start = time.time()
                    index_words = []

                    if items is None:
                        items = fn(filters)
                    else:
                        logging.warn("Detected update with %d items", len(items))
                    logging.debug("Simplifying %d items..", len(items))
                    items = json.loads(json.dumps(items, cls=JSONEncoder, separators=(',', ':')))
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
                    # for crop_at in xrange(min_word_length, max_letter[1]+1):
                    index.editable = True
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
                    index.editable = False
                    del items_ids
                    start = time.time()
                    logging.debug(
                        "Saving processed result with %d items in storage and %d items in index..",
                        len(items),
                        len(index)
                    )
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
                found = [[i, word, list(index[word].as_list())] for i, word in enumerate(query_words)]
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
                if not_found and min_word_length == 1:
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
                            queue.extend([item, suggestion, list(index[suggestion].as_list())] for suggestion in item_suggestions)
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
                        if suggestions: # If we already have suggestions, stops the loop!
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


def get_result(q):
    def wrap():
        result = q.get()
        q.put(result)
        if result["error"]:
            raise result["exception"]
        return result["result"]

    return wrap


def wait(q):
    def wrap():
        q.put(q.get())

    return wrap


def check_success(q):
    def wrap():
        result = q.get()
        q.put(result)
        if result["error"]:
            raise result["exception"]

    return wrap


def threaded(f, daemon=False):
    def wrapped_f(q, *args, **kwargs):
        '''this function calls the decorated function and puts the
        result in a queue'''
        try:
            ret = f(*args, **kwargs)
        except Exception, e:
            q.put({
                "error": True,
                "exception": e
            })
        else:
            q.put({
                "error": False,
                "result": ret
            })

    def wrap(*args, **kwargs):
        '''this is the function returned from the decorator. It fires off
        wrapped_f in a new thread and returns the thread object with
        the result queue attached'''

        q = Queue.Queue(1)

        t = threading.Thread(target=wrapped_f, args=(q,) + args, kwargs=kwargs)
        t.daemon = daemon
        t.start()
        t.get_result = get_result(q)
        t.check_success = check_success(q)
        t.wait = wait(q)
        return t

    return wrap
