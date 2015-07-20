import threading
import Queue

__author__ = 'fernando'


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
        """this function calls the decorated function and puts the
        result in a queue"""
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
        """this is the function returned from the decorator. It fires off
        wrapped_f in a new thread and returns the thread object with
        the result queue attached"""

        q = Queue.Queue(1)

        t = threading.Thread(target=wrapped_f, args=(q,) + args, kwargs=kwargs)
        t.daemon = daemon
        t.start()
        t.get_result = get_result(q)
        t.check_success = check_success(q)
        t.wait = wait(q)
        return t

    return wrap